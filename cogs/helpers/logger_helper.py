"""
Helper for consistent logger setup for Rudebot cogs.
Ensures each cog can have its own file handler and formatting.
"""
import logging
import os

def get_logger(name, log_file):
    """
    Set up and return a logger with a dedicated file handler for a cog.
    Avoids duplicate handlers if the cog is reloaded.
    """
    logger = logging.getLogger(name)
    log_dir = os.path.dirname(log_file)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not any(isinstance(h, logging.FileHandler) and h.baseFilename == os.path.abspath(log_file)
               for h in logger.handlers):
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger 