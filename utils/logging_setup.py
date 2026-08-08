import logging
import os


def configure_logging(level: str = "INFO"):
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    log_format = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=numeric_level, format=log_format)

    # Add a rotating file handler for persistent logs
    try:
        from logging.handlers import RotatingFileHandler

        logfile = "logs/agent.log"
        os.makedirs("logs", exist_ok=True)
        fh = RotatingFileHandler(logfile, maxBytes=5 * 1024 * 1024, backupCount=3)
        fh.setLevel(numeric_level)
        fh.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(fh)
    except Exception:
        logging.getLogger().warning(
            "Could not configure file logging; continuing with console only"
        )
