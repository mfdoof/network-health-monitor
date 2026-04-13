import logging
import os

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Log format
formatter = logging.Formatter(
    fmt="%(asctime)s %(levelname)-8s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# File handler - writes to logs/app.log
file_handler = logging.FileHandler("logs/app.log")
file_handler.setFormatter(formatter)

# Console handler - prints to terminal
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Create logger
logger = logging.getLogger("network_monitor")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)


