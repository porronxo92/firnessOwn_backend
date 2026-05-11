"""Configuración centralizada de logging para la API."""
import logging
import os


def configure_logging() -> None:
    """
    Configura el sistema de logging.
    - En producción: nivel WARNING o superior, formato JSON-friendly.
    - En desarrollo: nivel DEBUG, formato legible.
    """
    env = os.getenv("ENVIRONMENT", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO" if env == "production" else "DEBUG")

    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(
        level=getattr(logging, log_level.upper(), logging.INFO),
        format=fmt,
    )

    # Silenciar loggers muy verbosos de librerías externas
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
