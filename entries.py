"""Modèle des entrées du journal : tâches, événements et notes.

La classe abstraite :class:`Entry` regroupe ce qui est commun à toutes les
entrées. Chaque sous-classe définit son propre symbole de rapid logging
(polymorphisme) et ses propres règles.
"""

from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from datetime import date, datetime, time
from enum import Enum
from typing import Any, Optional

from bujo.exceptions import EmptyNameError, InvalidTransitionError

logger = logging.getLogger(__name__)


class TaskState(Enum):
    """États possibles d'une tâche."""

    TODO = "todo"
    DONE = "done"
    MIGRATED = "migrated"
    SCHEDULED = "scheduled"
    CANCELLED = "cancelled"


class Signifier(Enum):
    """Signifiants ajoutés devant une entrée pour la mettre en valeur."""

    PRIORITY = "*"
    IDEA = "!"


class Entry(ABC):
    """Classe de base abstraite de toutes les entrées du journal.

    :param name: nom court de l'entrée (obligatoire, non vide)
    :param description: texte libre facultatif
    :param log_date: date du log auquel l'entrée appartient
        (par défaut aujourd'hui)
    :param signifier: signifiant facultatif (priorité, idée)
    :raises EmptyNameError: si le nom est vide
    """

    def __init__(
        self,
        name: str,
        description: str = "",
        log_date: Optional[date] = None,
        signifier: Optional[Signifier] = None,
    ) -> None:
        """Initialise les attributs communs à toutes les entrées."""
        # L'identifiant est unique et ne change jamais : deux entrées peuvent
        # porter le même nom (cf. migration), on ne doit donc pas s'y fier.
        self._id: str = uuid.uuid4().hex
        self._created_at: datetime = datetime.now()
        self.name = name  # passe par le setter -> validation
        self.description: str = description
        self.log_date: date = log_date or date.today()
        self.signifier: Optional[Signifier] = signifier

    # --- Encapsulation ---------------------------------------------------
    @property
    def id(self) -> str:
        """Identifiant unique (lecture seule)."""
        return self._id

    @property
    def created_at(self) -> datetime:
        """Date et heure de création (lecture seule)."""
        return self._created_at

    @property
    def name(self) -> str:
        """Nom de l'entrée."""
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        """Modifie le nom après validation."""
        if not isinstance(value, str) or not value.strip():
            raise EmptyNameError("Le nom d'une entrée ne peut pas être vide.")
        self._name = value.strip()

    # --- Polymorphisme ----------------------------------------------------
    @property
    @abstractmethod
    def symbol(self) -> str:
        """Symbole de rapid logging propre au type d'entrée."""

    def render(self) -> str:
        """Retourne la ligne affichée dans un log (ex. ``* • Réviser``)."""
        prefix = f"{self.signifier.value} " if self.signifier else ""
        return f"{prefix}{self.symbol} {self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Sérialise l'entrée en dictionnaire (utile pour le JSON).

        Les sous-classes complètent ce dictionnaire avec leurs attributs.
        """
        return {
            "type": type(self).__name__,
            "id": self._id,
            "name": self._name,
            "description": self.description,
            "created_at": self._created_at.isoformat(),
            "log_date": self.log_date.isoformat(),
            "signifier": self.signifier.value if self.signifier else None,
        }

    # TODO (niveau 3) : classmethod from_dict(data) pour recharger une entrée
    # depuis le JSON, en restaurant l'id et created_at d'origine.

    def __repr__(self) -> str:
        """Représentation utile pour le débogage."""
        return f"{type(self).__name__}(id={self._id[:8]}, name={self._name!r})"


class Task(Entry):
    """Tâche : seule entrée qui possède un cycle de vie.

    Règle métier : seule une tâche à l'état ``TODO`` peut changer d'état.
    """

    _SYMBOLS: dict[TaskState, str] = {
        TaskState.TODO: "•",
        TaskState.DONE: "×",
        TaskState.MIGRATED: ">",
        TaskState.SCHEDULED: "<",
    }

    def __init__(
        self,
        name: str,
        description: str = "",
        log_date: Optional[date] = None,
        signifier: Optional[Signifier] = None,
        origin_id: Optional[str] = None,
    ) -> None:
        """Crée une tâche à l'état TODO.

        :param origin_id: id de la tâche dont celle-ci est issue par
            migration (None si c'est une tâche originale)
        """
        super().__init__(name, description, log_date, signifier)
        self._state: TaskState = TaskState.TODO
        self.origin_id: Optional[str] = origin_id

    @property
    def state(self) -> TaskState:
        """État courant (modifiable uniquement via les méthodes)."""
        return self._state

    @property
    def symbol(self) -> str:
        """Symbole selon l'état de la tâche."""
        return self._SYMBOLS.get(self._state, "•")

    def render(self) -> str:
        """Affiche la tâche ; une tâche abandonnée est barrée."""
        if self._state is TaskState.CANCELLED:
            prefix = f"{self.signifier.value} " if self.signifier else ""
            return f"{prefix}~~{self.name}~~"
        return super().render()

    def _transition(self, new_state: TaskState) -> None:
        """Applique un changement d'état en vérifiant la règle métier."""
        if self._state is not TaskState.TODO:
            logger.error(
                "Transition interdite %s -> %s pour %r",
                self._state.value, new_state.value, self,
            )
            raise InvalidTransitionError(
                f"Impossible de passer de {self._state.value} "
                f"à {new_state.value}."
            )
        logger.debug("%r : %s -> %s", self, self._state.value,
                     new_state.value)
        self._state = new_state

    def complete(self) -> None:
        """Marque la tâche comme terminée."""
        self._transition(TaskState.DONE)

    def cancel(self) -> None:
        """Abandonne la tâche (devenue sans objet)."""
        self._transition(TaskState.CANCELLED)

    def schedule(self) -> None:
        """Marque la tâche comme planifiée dans le Future Log."""
        # TODO (niveau 3) : recevoir le mois cible et l'ajouter au FutureLog
        self._transition(TaskState.SCHEDULED)

    def mark_migrated(self) -> None:
        """Marque la tâche comme migrée.

        Ne crée pas la nouvelle tâche : c'est le rôle du Journal, qui
        connaît le log cible (voir ``Journal.migrate_task``).
        """
        self._transition(TaskState.MIGRATED)

    def to_dict(self) -> dict[str, Any]:
        """Ajoute l'état et l'origine au dictionnaire de base."""
        data = super().to_dict()
        data["state"] = self._state.value
        data["origin_id"] = self.origin_id
        return data


class Event(Entry):
    """Événement : se produit à une date (et éventuellement une heure)."""

    def __init__(
        self,
        name: str,
        event_date: date,
        event_time: Optional[time] = None,
        description: str = "",
        signifier: Optional[Signifier] = None,
    ) -> None:
        """Crée un événement rattaché au log de sa date."""
        super().__init__(name, description, event_date, signifier)
        self.event_time: Optional[time] = event_time

    @property
    def symbol(self) -> str:
        """Symbole d'un événement."""
        return "○"

    def render(self) -> str:
        """Ajoute l'heure devant le nom si elle est connue."""
        if self.event_time is None:
            return super().render()
        prefix = f"{self.signifier.value} " if self.signifier else ""
        return f"{prefix}{self.symbol} {self.event_time:%H:%M} {self.name}"

    def to_dict(self) -> dict[str, Any]:
        """Ajoute l'heure au dictionnaire de base."""
        data = super().to_dict()
        data["event_time"] = (self.event_time.isoformat()
                              if self.event_time else None)
        return data


class Note(Entry):
    """Note : information, observation. Pas de cycle de vie."""

    @property
    def symbol(self) -> str:
        """Symbole d'une note."""
        return "–"
