import logging
import time
import functools
import os

# --- 1. GLOBAL LOGGING SWITCHES ---
MASTER_LOGGING_ENABLED = True
DEFAULT_LEVEL = logging.DEBUG

# --- 2. GRANULAR CONTROL ---
MODULE_CONFIG = {
    "src.nodes": logging.DEBUG,   
    "src.tools": logging.INFO,    
    "src.graph": logging.WARNING  
}

def get_logger(name):
    """
    Creates a logger that writes to BOTH the console and a file.
    """
    logger = logging.getLogger(name)
    
    # Global Kill Switch
    if not MASTER_LOGGING_ENABLED:
        logger.setLevel(logging.CRITICAL + 1)
        return logger

    # Set Level
    level = MODULE_CONFIG.get(name, DEFAULT_LEVEL)
    logger.setLevel(level)
    
    # Prevent adding duplicate handlers if get_logger is called twice
    if not logger.handlers:
        # --- HANDLER 1: CONSOLE (Terminal) ---
        c_handler = logging.StreamHandler()
        c_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] - %(message)s', datefmt='%H:%M:%S')
        c_handler.setFormatter(c_format)
        logger.addHandler(c_handler)

        # --- HANDLER 2: FILE (agent.log) ---
        # This creates 'agent.log' in your main folder
        f_handler = logging.FileHandler('agent.log', mode='a', encoding='utf-8') 
        f_format = logging.Formatter('%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')
        f_handler.setFormatter(f_format)
        logger.addHandler(f_handler)
        
    return logger

def log_execution_time(logger):
    """
    Decorator to log how long a function takes to run.
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
                raise e 
        return wrapper
    return decorator