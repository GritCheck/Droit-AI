"""
Comprehensive error logging and monitoring utilities
"""

import logging
import traceback
import json
import time
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum
from fastapi import Request, HTTPException
from starlette.responses import Response

from app.core.config import get_settings

settings = get_settings()


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """Error categories for classification"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    EXTERNAL_SERVICE = "external_service"
    SYSTEM = "system"
    NETWORK = "network"
    DATABASE = "database"
    SECURITY = "security"


class StructuredLogger:
    """Structured logging with correlation and context"""
    
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup logger with structured format"""
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    def _create_log_entry(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.LOW,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        **kwargs
    ) -> Dict[str, Any]:
        """Create structured log entry"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
            "severity": severity.value,
            "category": category.value,
            "service": "SentinelRAG",
            "environment": "development" if settings.debug else "production",
            **kwargs
        }
    
    def log_error(
        self,
        message: str,
        exception: Optional[Exception] = None,
        request: Optional[Request] = None,
        user_context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        category: ErrorCategory = ErrorCategory.SYSTEM,
        **kwargs
    ):
        """Log structured error with full context"""
        log_entry = self._create_log_entry(
            message=message,
            severity=severity,
            category=category,
            **kwargs
        )
        
        # Add exception details
        if exception:
            log_entry["exception"] = {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc()
            }
        
        # Add request context
        if request:
            log_entry["request"] = {
                "method": request.method,
                "url": str(request.url),
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client_ip": self._get_client_ip(request),
                "user_agent": request.headers.get("user-agent")
            }
        
        # Add user context
        if user_context:
            log_entry["user"] = {
                "user_id": user_context.get("user_id"),
                "tenant_id": user_context.get("tenant_id"),
                "groups_count": len(user_context.get("group_ids", []))
            }
        
        # Log with appropriate level
        if severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(json.dumps(log_entry, default=str))
        elif severity == ErrorSeverity.MEDIUM:
            self.logger.warning(json.dumps(log_entry, default=str))
        else:
            self.logger.info(json.dumps(log_entry, default=str))
    
    def log_security_event(
        self,
        event_type: str,
        message: str,
        request: Optional[Request] = None,
        user_context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """Log security-related events"""
        self.log_error(
            message=f"[SECURITY] {message}",
            request=request,
            user_context=user_context,
            severity=ErrorSeverity.HIGH,
            category=ErrorCategory.SECURITY,
            security_event=event_type,
            **kwargs
        )
    
    def log_performance(
        self,
        operation: str,
        duration: float,
        request: Optional[Request] = None,
        **kwargs
    ):
        """Log performance metrics"""
        log_entry = self._create_log_entry(
            message=f"Performance: {operation}",
            severity=ErrorSeverity.LOW,
            category=ErrorCategory.SYSTEM,
            operation=operation,
            duration_ms=duration * 1000,
            **kwargs
        )
        
        if request:
            log_entry["request"] = {
                "method": request.method,
                "path": request.url.path,
                "client_ip": self._get_client_ip(request)
            }
        
        self.logger.info(json.dumps(log_entry, default=str))
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        return request.client.host if request.client else "unknown"


class ErrorTracker:
    """Track and analyze errors for monitoring"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_patterns = {}
    
    def track_error(
        self,
        error_type: str,
        message: str,
        category: ErrorCategory,
        severity: ErrorSeverity
    ):
        """Track error occurrence"""
        key = f"{category.value}:{error_type}"
        
        # Increment count
        self.error_counts[key] = self.error_counts.get(key, 0) + 1
        
        # Store pattern
        if key not in self.error_patterns:
            self.error_patterns[key] = {
                "error_type": error_type,
                "category": category.value,
                "severity": severity.value,
                "sample_message": message,
                "count": 0,
                "first_seen": datetime.utcnow().isoformat()
            }
        
        self.error_patterns[key]["count"] += 1
        self.error_patterns[key]["last_seen"] = datetime.utcnow().isoformat()
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of tracked errors"""
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_patterns": dict(sorted(
                self.error_patterns.items(),
                key=lambda x: x[1]["count"],
                reverse=True
            )),
            "categories": {
                category: sum(1 for pattern in self.error_patterns.values() 
                            if pattern["category"] == category)
                for category in set(pattern["category"] for pattern in self.error_patterns.values())
            }
        }


# Global instances
structured_logger = StructuredLogger("sentinel_rag")
error_tracker = ErrorTracker()


def log_error(
    message: str,
    exception: Optional[Exception] = None,
    request: Optional[Request] = None,
    user_context: Optional[Dict[str, Any]] = None,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    category: ErrorCategory = ErrorCategory.SYSTEM,
    **kwargs
):
    """Convenience function for error logging"""
    structured_logger.log_error(
        message=message,
        exception=exception,
        request=request,
        user_context=user_context,
        severity=severity,
        category=category,
        **kwargs
    )
    
    # Track error for monitoring
    if exception:
        error_tracker.track_error(
            error_type=type(exception).__name__,
            message=message,
            category=category,
            severity=severity
        )


def log_security_event(
    event_type: str,
    message: str,
    request: Optional[Request] = None,
    user_context: Optional[Dict[str, Any]] = None,
    **kwargs
):
    """Convenience function for security event logging"""
    structured_logger.log_security_event(
        event_type=event_type,
        message=message,
        request=request,
        user_context=user_context,
        **kwargs
    )


def log_performance(operation: str, duration: float, request: Optional[Request] = None, **kwargs):
    """Convenience function for performance logging"""
    structured_logger.log_performance(
        operation=operation,
        duration=duration,
        request=request,
        **kwargs
    )


# Context manager for operation timing
class OperationTimer:
    """Context manager for timing operations"""
    
    def __init__(self, operation: str, request: Optional[Request] = None, **kwargs):
        self.operation = operation
        self.request = request
        self.kwargs = kwargs
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            log_performance(
                operation=self.operation,
                duration=duration,
                request=self.request,
                **self.kwargs
            )
        
        if exc_type:
            log_error(
                message=f"Operation failed: {self.operation}",
                exception=exc_val,
                request=self.request,
                severity=ErrorSeverity.MEDIUM,
                category=ErrorCategory.BUSINESS_LOGIC,
                operation=self.operation,
                **self.kwargs
            )
