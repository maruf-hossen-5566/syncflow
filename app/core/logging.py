import logging


def setup_logger(name: str = __name__, log_file: str = "app.log"):
    """Configure and return a logger with file and console handlers.

    Args:
        name (str): Name of the logger (default: __name__).
        log_file (str): Path to the log file (default: "app.log").
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)  # Set root logger level

    # Clear existing handlers to avoid duplicate logs
    logger.handlers.clear()

    # Format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


# Default logger for the module
logger = setup_logger()
