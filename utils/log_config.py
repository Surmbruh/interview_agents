"""
Centralized logging configuration for Interview Coach.
Provides consistent logging across all modules.
"""
import logging
import sys
from typing import Optional


def setup_logging(level: str = "INFO", log_file: Optional[str] = None) -> None:
    """
    Configure logging for the entire application.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path to write logs to
    """
    log_format = "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Console handler with colored output (if terminal supports it)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(ColoredFormatter(log_format, date_format))
    root_logger.addHandler(console_handler)
    
    # Optional file handler
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter(log_format, date_format))
        root_logger.addHandler(file_handler)
    
    # Reduce noise from external libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)
    logging.getLogger("langchain").setLevel(logging.WARNING)


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",     # Cyan
        "INFO": "\033[32m",      # Green
        "WARNING": "\033[33m",   # Yellow
        "ERROR": "\033[31m",     # Red
        "CRITICAL": "\033[35m",  # Magenta
        "RESET": "\033[0m"       # Reset
    }
    
    # Agent-specific colors for easy identification
    AGENT_COLORS = {
        "router": "\033[96m",       # Light Cyan
        "observer": "\033[94m",     # Light Blue
        "interviewer": "\033[93m",  # Light Yellow
        "critic": "\033[95m",       # Light Magenta
        "planner": "\033[92m",      # Light Green
        "manager": "\033[91m",      # Light Red
        "feedback": "\033[97m",     # White
    }
    
    def format(self, record: logging.LogRecord) -> str:
        # Get color based on level
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        # Check if this is an agent logger and apply agent-specific color
        logger_name = record.name.lower()
        for agent, agent_color in self.AGENT_COLORS.items():
            if agent in logger_name:
                color = agent_color
                break
        
        # Format the message
        original = super().format(record)
        
        # Only colorize if outputting to a terminal
        if sys.stdout.isatty():
            return f"{color}{original}{reset}"
        return original


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    Use this instead of logging.getLogger() directly.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
