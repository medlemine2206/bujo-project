"""bujo : bibliothèque Python de Bullet Journal."""

import logging

from bujo.entries import Entry, Event, Note, Signifier, Task, TaskState
from bujo.exceptions import (
    BujoError,
    EmptyNameError,
    EntryNotFoundError,
    InvalidDateError,
    InvalidTransitionError,
)
from bujo.journal import Journal
from bujo.logging_config import setup_logging

__version__ = "0.1.0"

# Bonne pratique pour une bibliothèque : ne rien afficher par défaut,
# c'est l'application qui décide (via setup_logging).
logging.getLogger(__name__).addHandler(logging.NullHandler())

__all__ = [
    "Entry", "Event", "Note", "Signifier", "Task", "TaskState", "Journal",
    "BujoError", "EmptyNameError", "EntryNotFoundError", "InvalidDateError",
    "InvalidTransitionError", "setup_logging",
]
