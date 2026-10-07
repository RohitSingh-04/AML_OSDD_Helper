from .settings import BASE_DIR
import sys
import logging

LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "aml_osdd_logs.log"

logger = logging.getLogger("aml_osdd")
logger.setLevel(logging.INFO)

log_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Terminal handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# File handler
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)

# Prevent duplicate log messages in root logger
logger.propagate = False
