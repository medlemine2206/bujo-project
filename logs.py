"""Organisation des entrées en logs (Daily Log, Monthly Log...)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from typing import Iterator

from bujo.entries import Entry, Task, TaskState
from bujo.exceptions import EntryNotFoundError, InvalidDateError


class BaseLog(ABC):
    """Page du journal contenant des entrées.

    Les entrées sont stockées dans un dictionnaire ``id -> Entry`` :
    accès, ajout et suppression en O(1), et l'ordre d'insertion est
    conservé (dict ordonné depuis Python 3.7) pour l'affichage.
    """

    def __init__(self) -> None:
        """Initialise un log vide."""
        self._entries: dict[str, Entry] = {}

    @property
    @abstractmethod
    def title(self) -> str:
        """Titre affiché en en-tête du log."""

    def add(self, entry: Entry) -> None:
        """Ajoute une entrée au log."""
        self._entries[entry.id] = entry

    def remove(self, entry_id: str) -> Entry:
        """Retire et retourne l'entrée d'identifiant ``entry_id``."""
        try:
            return self._entries.pop(entry_id)
        except KeyError:
            raise EntryNotFoundError(entry_id) from None

    def get(self, entry_id: str) -> Entry:
        """Retourne l'entrée d'identifiant ``entry_id``."""
        try:
            return self._entries[entry_id]
        except KeyError:
            raise EntryNotFoundError(entry_id) from None

    def __contains__(self, entry_id: object) -> bool:
        """Permet d'écrire ``entry_id in log``."""
        return entry_id in self._entries

    def __iter__(self) -> Iterator[Entry]:
        """Permet d'écrire ``for entry in log``."""
        return iter(self._entries.values())

    def __len__(self) -> int:
        """Nombre d'entrées du log."""
        return len(self._entries)

    def pending_tasks(self) -> list[Task]:
        """Retourne les tâches encore à faire (état TODO)."""
        return [e for e in self if isinstance(e, Task)
                and e.state is TaskState.TODO]

    def render(self) -> str:
        """Affiche le log en rapid logging (titre + une ligne par entrée).

        TODO (niveau 2) : améliorer (tri événements/tâches, descriptions,
        option pour masquer les tâches terminées...).
        """
        lines = [f"# {self.title}"]
        lines += [entry.render() for entry in self]
        return "\n".join(lines)


class DailyLog(BaseLog):
    """Journal d'une journée."""

    def __init__(self, day: date) -> None:
        """Crée le log du jour ``day``."""
        super().__init__()
        self.day: date = day

    @property
    def title(self) -> str:
        """Titre du type ``Lundi 23/11/2026``."""
        return self.day.strftime("%d/%m/%Y")


class MonthlyLog(BaseLog):
    """Vue d'un mois : tâches du mois (le calendrier vient au niveau 2)."""

    def __init__(self, year: int, month: int) -> None:
        """Crée le log du mois ``month`` de l'année ``year``."""
        if not 1 <= month <= 12:
            raise InvalidDateError(f"Mois invalide : {month}")
        super().__init__()
        self.year: int = year
        self.month: int = month

    @property
    def title(self) -> str:
        """Titre du type ``11/2026``."""
        return f"{self.month:02d}/{self.year}"

    # TODO (niveau 2) : méthode calendar() qui affiche les jours du mois
    # avec les événements (voir le module standard ``calendar``).


# TODO (niveau 3) : class FutureLog(BaseLog) -> entrées rangées par mois futur
# TODO (niveau 3) : class Collection(BaseLog) -> page libre avec un nom
