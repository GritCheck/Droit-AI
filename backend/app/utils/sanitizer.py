"""
Input sanitization utilities for security
"""

import re
import html
import logging
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class InputSanitizer:
    """Comprehensive input sanitization for security"""
    
    # Dangerous patterns to detect and remove
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript URLs
        r'vbscript:',                  # VBScript URLs
        r'data:text/html',            # Data URLs
        r'on\w+\s*=',                # Event handlers
        r'expression\s*\(',          # CSS expressions
        r'@import',                   # CSS imports
        r'eval\s*\(',                # eval() calls
        r'exec\s*\(',                # exec() calls
        r'system\s*\(',              # system() calls
        r'shell_exec\s*\(',          # shell_exec() calls
        r'passthru\s*\(',            # passthru() calls
        r'file_get_contents\s*\(',   # file operations
        r'fopen\s*\(',               # file operations
        r'unlink\s*\(',              # file deletion
        r'rmdir\s*\(',               # directory deletion
        r'mkdir\s*\(',               # directory creation
        r'chmod\s*\(',               # permission changes
        r'chown\s*\(',               # ownership changes
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)',
        r'(--|#|/\*|\*/)',           # SQL comments
        r'(\bOR\b.*\b1\s*=\s*1\b)',  # Always true conditions
        r'(\bAND\b.*\b1\s*=\s*1\b)', # Always true conditions
        r'(\'\s*OR\s*\'.*\')',        # String-based injection
        r'(\\"\s*OR\s*\\".*)',        # Double-quoted injection
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r'<iframe',
        r'<object',
        r'<embed',
        r'<link',
        r'<meta',
        r'<style',
        r'<img[^>]*src[^>]*javascript:',
        r'<div[^>]*on\w+=',
        r'<span[^>]*on\w+=',
    ]
    
    @classmethod
    def sanitize_string(cls, input_str: str, max_length: int = 2000) -> str:
        """Sanitize string input"""
        if not isinstance(input_str, str):
            return str(input_str)
        
        # Trim to max length
        if len(input_str) > max_length:
            input_str = input_str[:max_length]
            logger.warning(f"Input truncated to {max_length} characters")
        
        # HTML encode
        sanitized = html.escape(input_str)
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove XSS patterns
        for pattern in cls.XSS_PATTERNS:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        # Remove control characters except newlines and tabs
        sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', sanitized)
        
        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_search_query(cls, query: str) -> str:
        """Sanitize search query specifically"""
        if not isinstance(query, str):
            return str(query)
        
        # Basic string sanitization
        sanitized = cls.sanitize_string(query, max_length=500)
        
        # Remove search-specific dangerous patterns
        search_dangerous = [
            r'\.\./',                    # Directory traversal
            r'\.\.\\',                   # Directory traversal (Windows)
            r'[<>]',                     # Angle brackets
            r'[|&;`$]',                 # Shell metacharacters
            r'\bNULL\b',                 # SQL NULL
            r'\bUNION\b',               # SQL UNION
        ]
        
        for pattern in search_dangerous:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for security"""
        if not isinstance(filename, str):
            return str(filename)
        
        # Remove dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '', filename)
        
        # Remove path traversal attempts
        sanitized = re.sub(r'\.\.[\\/]', '', sanitized)
        
        # Limit length
        if len(sanitized) > 255:
            sanitized = sanitized[:255]
        
        # Ensure it's not empty after sanitization
        if not sanitized.strip():
            sanitized = "uploaded_file"
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_group_id(cls, group_id: str) -> str:
        """Sanitize group ID for security"""
        if not isinstance(group_id, str):
            return str(group_id)
        
        # Only allow alphanumeric, hyphens, and underscores
        sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', group_id)
        
        # Limit length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]
        
        return sanitized.strip()
    
    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], max_depth: int = 5) -> Dict[str, Any]:
        """Recursively sanitize dictionary values"""
        if max_depth <= 0:
            logger.warning("Maximum recursion depth reached in sanitization")
            return {}
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize keys
            safe_key = cls.sanitize_string(str(key), max_length=100)
            
            # Sanitize values based on type
            if isinstance(value, str):
                sanitized[safe_key] = cls.sanitize_string(value)
            elif isinstance(value, (int, float, bool)):
                sanitized[safe_key] = value
            elif isinstance(value, dict):
                sanitized[safe_key] = cls.sanitize_dict(value, max_depth - 1)
            elif isinstance(value, list):
                sanitized[safe_key] = cls.sanitize_list(value, max_depth - 1)
            else:
                # Convert other types to string and sanitize
                sanitized[safe_key] = cls.sanitize_string(str(value))
        
        return sanitized
    
    @classmethod
    def sanitize_list(cls, data: List[Any], max_depth: int = 5) -> List[Any]:
        """Recursively sanitize list values"""
        if max_depth <= 0:
            logger.warning("Maximum recursion depth reached in sanitization")
            return []
        
        sanitized = []
        for item in data:
            if isinstance(item, str):
                sanitized.append(cls.sanitize_string(item))
            elif isinstance(item, (int, float, bool)):
                sanitized.append(item)
            elif isinstance(item, dict):
                sanitized.append(cls.sanitize_dict(item, max_depth - 1))
            elif isinstance(item, list):
                sanitized.append(cls.sanitize_list(item, max_depth - 1))
            else:
                # Convert other types to string and sanitize
                sanitized.append(cls.sanitize_string(str(item)))
        
        return sanitized
    
    @classmethod
    def validate_and_sanitize(cls, input_data: Any, input_type: str = "string") -> Any:
        """Validate and sanitize input based on type"""
        if input_data is None:
            return None
        
        if input_type == "string":
            return cls.sanitize_string(str(input_data))
        elif input_type == "search_query":
            return cls.sanitize_search_query(str(input_data))
        elif input_type == "filename":
            return cls.sanitize_filename(str(input_data))
        elif input_type == "group_id":
            return cls.sanitize_group_id(str(input_data))
        elif input_type == "dict":
            if isinstance(input_data, dict):
                return cls.sanitize_dict(input_data)
            else:
                return {}
        elif input_type == "list":
            if isinstance(input_data, list):
                return cls.sanitize_list(input_data)
            else:
                return []
        else:
            return cls.sanitize_string(str(input_data))


def sanitize_input(input_data: Any, input_type: str = "string") -> Any:
    """Convenience function for input sanitization"""
    return InputSanitizer.validate_and_sanitize(input_data, input_type)


# Pydantic validator for automatic sanitization
class SanitizedModel(BaseModel):
    """Base model with automatic input sanitization"""
    
    class Config:
        validate_assignment = True
    
    def __init__(self, **data):
        # Sanitize input data before validation
        sanitized_data = InputSanitizer.sanitize_dict(data)
        super().__init__(**sanitized_data)
