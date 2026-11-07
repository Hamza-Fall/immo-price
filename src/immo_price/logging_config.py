"""Configuration de la journalisation."""

import logging


def setup_logging(level: str = "INFO") -> None:
    """Configure le format et le niveau des logs.

    Args:
        level: Niveau de log (DEBUG, INFO, WARNING, ERROR).
    """
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        force=True,
    )
