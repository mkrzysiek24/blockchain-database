DEBUG = 0


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG" if DEBUG else "INFO",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG" if DEBUG else "INFO",
            "formatter": "default",
            "filename": "app.log",
        },
    },
    "root": {
        "level": "DEBUG" if DEBUG else "INFO",
        "handlers": ["console", "file"],
    },
}
