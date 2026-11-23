"""Exceptions personnalisées de la bibliothèque bujo.

Toutes héritent de :class:`BujoError`, ce qui permet à un utilisateur de la
bibliothèque d'attraper toutes nos erreurs d'un coup avec ``except BujoError``.
"""


class BujoError(Exception):
    """Classe de base de toutes les erreurs de la bibliothèque."""


class EmptyNameError(BujoError, ValueError):
    """Levée quand une entrée est créée avec un nom vide."""


class InvalidDateError(BujoError, ValueError):
    """Levée quand une date est invalide ou incohérente."""


class EntryNotFoundError(BujoError, KeyError):
    """Levée quand aucune entrée ne correspond à l'identifiant demandé."""


class InvalidTransitionError(BujoError):
    """Levée lors d'un changement d'état interdit.

    Exemples : terminer une tâche abandonnée, migrer une note.
    """
