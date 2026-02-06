import logging
import time
import functools
import os

# --- 1. GLOBAL LOGGING SWITCHES ---
# MASTER_LOGGING_ENABLED: If False, NO logs will appear anywhere.
MASTER_LOGGING_ENABLED = True

# DEFAULT_LEVEL: The standard level for all files (DEBUG shows everything, INFO shows less, ERROR shows only failures)
# Levels: logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR
DEFAULT_LEVEL = logging.DEBUG

# --- 2. GRANULAR CONTROL ---
# You can override the log level for specific files here.
# Example: "src.tools": logging.ERROR (Only show errors for tools, hide timing/debug info)
MODULE_CONFIG = {
    "src.nodes": logging.DEBUG,   # Show everything for nodes
    "src.tools": logging.INFO,    # Only show INFO and ERRORS for tools (hide debug data)
    "src.graph": logging.WARNING  # Only show warnings/errors for the graph
}

def get_logger(name):
    """
    Creates a logger for a specific file with the configured level.
    """
    logger = logging.getLogger(name)
    
    # If logging is globally disabled, set to CRITICAL+1 (silence everything)
    if not MASTER_LOGGING_ENABLED:
        logger.setLevel(logging.CRITICAL + 1)
        return logger

    # Set specific level if defined in MODULE_CONFIG, else use default
    level = MODULE_CONFIG.get(name, DEFAULT_LEVEL)
    logger.setLevel(level)
    
    # Create console handler if not exists
    if not logger.handlers:
        handler = logging.StreamHandler()
        # Format: [Time] [Level] [File] - Message
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] - %(message)s', datefmt='%H:%M:%S')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger

def log_execution_time(logger):
    """
    Decorator to log how long a function takes to run.
    Usage: @log_execution_time(logger)
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                duration = end_time - start_time
                logger.info(f"⏱️ {func.__name__} finished in {duration:.2f}s")
                return result
            except Exception as e:
                logger.error(f"❌ Error in {func.__name__}: {str(e)}", exc_info=True)
                raise e # Re-raise to handle it in the main code
        return wrapper
    return decorator