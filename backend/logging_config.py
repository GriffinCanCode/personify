"""
Modern structured logging configuration for 2025.
Uses structlog for JSON logging, context binding, and observability.
"""
import logging
import sys
from typing import Any, Dict, Optional
import structlog
from structlog.types import EventDict, Processor
from pythonjsonlogger import jsonlogger
import os
from datetime import datetime


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record['timestamp'] = datetime.utcnow().isoformat()
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno


def add_app_context(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add application context to all log entries"""
    event_dict['service'] = 'personify-backend'
    event_dict['environment'] = os.getenv('ENVIRONMENT', 'development')
    return event_dict


def add_request_id(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Add request ID from context if available"""
    from contextvars import ContextVar
    
    request_id_var: ContextVar[Optional[str]] = ContextVar('request_id', default=None)
    request_id = request_id_var.get()
    if request_id:
        event_dict['request_id'] = request_id
    return event_dict


def drop_color_message_key(logger: logging.Logger, method_name: str, event_dict: EventDict) -> EventDict:
    """Drop the color_message key from the event dict"""
    event_dict.pop('color_message', None)
    return event_dict


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = True,
    log_file: Optional[str] = None
) -> None:
    """
    Configure structlog with best practices for production use.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_logs: If True, output JSON logs; if False, use human-readable format
        log_file: Optional file path to write logs to
    """
    
    # Determine log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Shared processors for all configurations
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        add_app_context,
        add_request_id,
        drop_color_message_key,
    ]
    
    # Configure handlers
    handlers: list[logging.Handler] = []
    
    # Console handler
    if json_logs:
        # JSON logging for production
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        ))
        handlers.append(console_handler)
    else:
        # Human-readable logging for development
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s [%(levelname)s] %(name)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        handlers.append(console_handler)
    
    # File handler (if specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s'
        ))
        handlers.append(file_handler)
    
    # Configure standard library logging
    logging.basicConfig(
        handlers=handlers,
        level=numeric_level,
        format='%(message)s'
    )
    
    # Configure structlog
    if json_logs:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    
    structlog.configure(
        processors=shared_processors + [
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure structlog processor for stdlib
    structlog.stdlib.ProcessorFormatter.processor = structlog.stdlib.ProcessorFormatter.wrap_for_formatter
    
    # Silence noisy loggers
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.
    
    Args:
        name: Logger name (typically __name__)
    
    Returns:
        Configured structlog logger
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("user_logged_in", user_id=123, ip="192.168.1.1")
    """
    return structlog.get_logger(name)


# Context management for request tracking
class LogContext:
    """Context manager for adding context to logs"""
    
    def __init__(self, **kwargs):
        self.context = kwargs
    
    def __enter__(self):
        structlog.contextvars.bind_contextvars(**self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.unbind_contextvars(*self.context.keys())


def log_function_call(logger: structlog.stdlib.BoundLogger):
    """
    Decorator to automatically log function calls with arguments and results.
    
    Example:
        >>> @log_function_call(logger)
        >>> def my_function(arg1, arg2):
        >>>     return arg1 + arg2
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(
                f"calling_{func.__name__}",
                function=func.__name__,
                args=args[:3] if len(args) <= 3 else f"{args[:3]}...",  # Limit arg logging
                kwargs={k: v for k, v in list(kwargs.items())[:5]}  # Limit kwarg logging
            )
            try:
                result = func(*args, **kwargs)
                logger.debug(f"completed_{func.__name__}", function=func.__name__)
                return result
            except Exception as e:
                logger.error(
                    f"error_in_{func.__name__}",
                    function=func.__name__,
                    error=str(e),
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


def log_async_function_call(logger: structlog.stdlib.BoundLogger):
    """
    Decorator to automatically log async function calls.
    
    Example:
        >>> @log_async_function_call(logger)
        >>> async def my_async_function(arg1):
        >>>     return await some_operation(arg1)
    """
    def decorator(func):
        from functools import wraps
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            logger.debug(
                f"calling_{func.__name__}",
                function=func.__name__,
                args=args[:3] if len(args) <= 3 else f"{args[:3]}...",
                kwargs={k: v for k, v in list(kwargs.items())[:5]}
            )
            try:
                result = await func(*args, **kwargs)
                logger.debug(f"completed_{func.__name__}", function=func.__name__)
                return result
            except Exception as e:
                logger.error(
                    f"error_in_{func.__name__}",
                    function=func.__name__,
                    error=str(e),
                    exc_info=True
                )
                raise
        
        return wrapper
    return decorator


# Performance monitoring
class PerformanceTimer:
    """Context manager for timing operations"""
    
    def __init__(self, logger: structlog.stdlib.BoundLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None
    
    def __enter__(self):
        import time
        self.start_time = time.perf_counter()
        self.logger.debug(f"starting_{self.operation}", operation=self.operation, **self.context)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        duration_ms = (time.perf_counter() - self.start_time) * 1000
        
        if exc_type:
            self.logger.error(
                f"failed_{self.operation}",
                operation=self.operation,
                duration_ms=duration_ms,
                error=str(exc_val),
                **self.context
            )
        else:
            self.logger.info(
                f"completed_{self.operation}",
                operation=self.operation,
                duration_ms=duration_ms,
                **self.context
            )

