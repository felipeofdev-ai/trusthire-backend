"""
TrustHire Structured Logging
Production-grade JSON logging with context
"""

import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
from config import settings


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Human-readable format for development"""
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname[:4]
        message = record.getMessage()
        
        # Add extra fields if present
        extra = ""
        if hasattr(record, "extra"):
            extra = " | " + " ".join(f"{k}={v}" for k, v in record.extra.items())
        
        return f"[{timestamp}] {level} {record.name}: {message}{extra}"


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger instance
    
    Args:
        name: Logger name (usually module name)
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # Set level from config
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(level)
    
    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    
    # Set formatter based on config
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger


# Convenience function for adding context
def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """Log message with additional context fields"""
    extra_record = type('obj', (object,), {'extra': context})
    log_func = getattr(logger, level.lower())
    log_func(message, extra=extra_record)
