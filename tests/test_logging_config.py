"""Tests de la journalisation."""

import logging

from immo_price.logging_config import setup_logging


def test_setup_logging_sets_level() -> None:
    root = logging.getLogger()
    previous = root.level
    try:
        setup_logging("debug")
        assert root.level == logging.DEBUG
    finally:
        root.setLevel(previous)
