# Setup logging for bot

import logging
from pathlib import Path
from config import LOG_DIR

FULL_LOG_DIR = LOG_DIR / "full"
ERROR_LOG_DIR = LOG_DIR / "errors"
FULL_LOG_DIR.mkdir(exist_ok=True)
ERROR_LOG_DIR.mkdir(exist_ok=True)

# Full log
full_logger = logging.getLogger("full_logger")
full_logger.setLevel(logging.INFO)
fh = logging.FileHandler(FULL_LOG_DIR / "full.log", encoding="utf-8")
fh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
full_logger.addHandler(fh)
full_logger.addHandler(logging.StreamHandler())

# Error log
error_logger = logging.getLogger("error_logger")
error_logger.setLevel(logging.ERROR)
eh = logging.FileHandler(ERROR_LOG_DIR / "errors.log", encoding="utf-8")
eh.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
error_logger.addHandler(eh)
error_logger.addHandler(logging.StreamHandler())
