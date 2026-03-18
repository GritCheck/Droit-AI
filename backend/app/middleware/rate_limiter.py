"""
Rate limiting middleware for API endpoints
Implements token bucket and sliding window rate limiting
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class RateLimitConfig:
    """Rate limit configuration per endpoint"""
    requests_per_minute: int
    requests_per_hour: int
    burst_size: int


# Default rate limit configurations
RATE_LIMITS = {
    "/chat/ask": RateLimitConfig(requests_per_minute=20, requests_per_hour=200, burst_size=5),
    "/search/hybrid": RateLimitConfig(requests_per_minute=30, requests_per_hour=300, burst_size=10),
    "/ingestion/upload": RateLimitConfig(requests_per_minute=10, requests_per_hour=50, burst_size=3),
    "/default": RateLimitConfig(requests_per_minute=60, requests_per_hour=1000, burst_size=20)
}


class TokenBucket:
    """Token bucket implementation for rate limiting"""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = capacity
        self.last_refill = time.time()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens, return True if successful"""
        current_time = time.time()
        
        # Refill tokens based on elapsed time
        elapsed = current_time - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = current_time
        
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False


class SlidingWindowCounter:
    """Sliding window counter for rate limiting"""
    
    def __init__(self, window_size: int):
        self.window_size = window_size  # in seconds
        self.requests = defaultdict(deque)
    
    def add_request(self, key: str) -> int:
        """Add a request and return current count"""
        current_time = time.time()
        request_queue = self.requests[key]
        
        # Remove old requests outside the window
        while request_queue and request_queue[0] < current_time - self.window_size:
            request_queue.popleft()
        
        request_queue.append(current_time)
        return len(request_queue)
    
    def get_count(self, key: str) -> int:
        """Get current request count for key"""
        current_time = time.time()
        request_queue = self.requests[key]
        
        # Remove old requests outside the window
        while request_queue and request_queue[0] < current_time - self.window_size:
            request_queue.popleft()
        
        return len(request_queue)


class RateLimiter:
    """Main rate limiter combining multiple strategies"""
    
    def __init__(self):
        # Token buckets for burst control
        self.minute_buckets: Dict[str, TokenBucket] = {}
        self.hour_buckets: Dict[str, TokenBucket] = {}
        
        # Sliding windows for sustained rate control
        self.minute_counter = SlidingWindowCounter(60)  # 1 minute window
        self.hour_counter = SlidingWindowCounter(3600)  # 1 hour window
    
    def _get_client_key(self, request: Request) -> str:
        """Extract client identifier for rate limiting"""
        # Priority order: user ID from token, then IP address
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        else:
            ip = request.client.host if request.client else "unknown"
        
        # Try to get user ID from authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            # For simplicity, use a hash of the token as user identifier
            # In production, extract actual user ID from validated token
            import hashlib
            token_hash = hashlib.sha256(auth_header[7:].encode()).hexdigest()[:16]
            return f"user:{token_hash}"
        
        return f"ip:{ip}"
    
    def _get_rate_limit_config(self, path: str) -> RateLimitConfig:
        """Get rate limit configuration for endpoint"""
        # Find matching path (use most specific match)
        for pattern, config in RATE_LIMITS.items():
            if pattern != "/default" and path.startswith(pattern):
                return config
        return RATE_LIMITS["/default"]
    
    def check_rate_limit(self, request: Request) -> Tuple[bool, Optional[str]]:
        """Check if request is within rate limits"""
        client_key = self._get_client_key(request)
        path = request.url.path
        config = self._get_rate_limit_config(path)
        
        # Initialize buckets if needed
        if client_key not in self.minute_buckets:
            self.minute_buckets[client_key] = TokenBucket(
                capacity=config.burst_size,
                refill_rate=config.requests_per_minute / 60.0
            )
        
        if client_key not in self.hour_buckets:
            self.hour_buckets[client_key] = TokenBucket(
                capacity=config.requests_per_hour,
                refill_rate=config.requests_per_hour / 3600.0
            )
        
        # Check minute rate limit
        minute_count = self.minute_counter.add_request(client_key)
        if minute_count > config.requests_per_minute:
            logger.warning(f"Rate limit exceeded (minute): {client_key} - {minute_count}/{config.requests_per_minute}")
            return False, f"Rate limit exceeded: {config.requests_per_minute} requests per minute"
        
        # Check hour rate limit
        hour_count = self.hour_counter.add_request(client_key)
        if hour_count > config.requests_per_hour:
            logger.warning(f"Rate limit exceeded (hour): {client_key} - {hour_count}/{config.requests_per_hour}")
            return False, f"Rate limit exceeded: {config.requests_per_hour} requests per hour"
        
        # Check burst limit using token bucket
        if not self.minute_buckets[client_key].consume():
            logger.warning(f"Burst rate limit exceeded: {client_key}")
            return False, "Too many requests in quick succession"
        
        return True, None


class RateLimitMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for rate limiting"""
    
    def __init__(self, app, rate_limiter: Optional[RateLimiter] = None):
        super().__init__(app)
        self.rate_limiter = rate_limiter or RateLimiter()
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for health checks and static files
        if (request.url.path.startswith("/health") or 
            request.url.path.startswith("/metrics") or
            request.url.path.endswith((".css", ".js", ".ico", ".png", ".jpg"))):
            return await call_next(request)
        
        # Check rate limits
        is_allowed, reason = self.rate_limiter.check_rate_limit(request)
        
        if not is_allowed:
            # Add rate limit headers
            headers = {
                "X-RateLimit-Limit": str(60),  # Default per-minute limit
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + 60),
                "Retry-After": "60"
            }
            
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=reason,
                headers=headers
            )
        
        # Add rate limit headers for successful requests
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = "60"
        response.headers["X-RateLimit-Remaining"] = "59"  # Simplified for demo
        
        return response


# Global rate limiter instance
rate_limiter = RateLimiter()


def get_rate_limiter() -> RateLimiter:
    """Get global rate limiter instance"""
    return rate_limiter
