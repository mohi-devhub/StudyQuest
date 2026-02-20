"""
Structured JSON logger for production-ready logging.
Replaces print() statements with structured, contextual logging.
"""

import logging
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_data = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra context if provided
        if hasattr(record, 'context') and record.context:
            log_data['context'] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class StructuredLogger:
    """
    Structured logger that outputs JSON-formatted logs.
    
    Usage:
        logger = StructuredLogger(__name__)
        logger.info("User logged in", user_id="123", action="login")
        logger.error("Failed to generate quiz", topic="Python", error="API timeout")
    """
    
    def __init__(self, name: str):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name (typically __name__ of the module)
        """
        self.logger = logging.getLogger(name)
        
        # Configure log level from environment variable
        log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
        self.logger.setLevel(getattr(logging, log_level, logging.INFO))
        
        # Avoid duplicate handlers
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(JSONFormatter())
            self.logger.addHandler(handler)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _log(self, level: int, message: str, **context: Any) -> None:
        """
        Internal logging method that adds context.
        
        Args:
            level: Logging level
            message: Log message
            **context: Additional context as keyword arguments
        """
        extra = {'context': context} if context else {}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **context: Any) -> None:
        """
        Log debug message with optional context.
        
        Args:
            message: Debug message
            **context: Additional context (e.g., user_id="123", topic="Python")
        """
        self._log(logging.DEBUG, message, **context)
    
    def info(self, message: str, **context: Any) -> None:
        """
        Log info message with optional context.
        
        Args:
            message: Info message
            **context: Additional context (e.g., user_id="123", action="login")
        """
        self._log(logging.INFO, message, **context)
    
    def warning(self, message: str, **context: Any) -> None:
        """
        Log warning message with optional context.
        
        Args:
            message: Warning message
            **context: Additional context (e.g., user_id="123", issue="rate_limit")
        """
        self._log(logging.WARNING, message, **context)
    
    def error(self, message: str, **context: Any) -> None:
        """
        Log error message with optional context.
        
        Args:
            message: Error message
            **context: Additional context (e.g., user_id="123", error="timeout")
        """
        self._log(logging.ERROR, message, **context)
    
    def exception(self, message: str, **context: Any) -> None:
        """
        Log exception with traceback and optional context.
        
        Args:
            message: Exception message
            **context: Additional context
        """
        extra = {'context': context} if context else {}
        self.logger.exception(message, extra=extra)


# Convenience function to create logger instances
def get_logger(name: str) -> StructuredLogger:
    """
    Get a structured logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        StructuredLogger instance
    """
    return StructuredLogger(name)
