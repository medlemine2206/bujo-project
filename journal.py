"""Classe Journal : point d'entrée principal de la bibliothèque."""

from __future__ import annotations

import logging
from datetime import date, time
from typing import Optional

from bujo.entries import Entry, Event, Note, Signifier, Task
from bujo.exceptions import EntryNotFoundError, InvalidTransitionError
from bujo.logs import BaseLog, DailyLog, MonthlyLog

logger = logging.getLogger(__name__)


class Journal:
    """Bullet Journal complet.

    Exemple ::

        journal = Journal()
        t = journal.add_task("Réviser pytest", "chapitre fixtures")
        journal.complete_task(t.id)
        print(journal.daily_log().render())
    """

    def __init__(self) -> None:
        """Crée un journal vide."""
        self._daily_logs: dict[date, DailyLog] = {}
        self._monthly_logs: dict[tuple[int, int], MonthlyLog] = {}
        # Index id -> log contenant l'entrée : retrouver une entrée par son
        # id sans parcourir tous les logs.
        self._index: dict[str, BaseLog] = {}

    # --- Accès aux logs ---------------------------------------------------
    def daily_log(self, day: Optional[date] = None) -> DailyLog:
        """Retourne le Daily Log du jour (le crée s'il n'existe pas)."""
        day = day or date.today()
        if day not in self._daily_logs:
            self._daily_logs[day] = DailyLog(day)
            logger.debug("Création du Daily Log %s", day)
        return self._daily_logs[day]

    def monthly_log(self, year: int, month: int) -> MonthlyLog:
        """Retourne le Monthly Log du mois (le crée s'il n'existe pas)."""
        key = (year, month)
        if key not in self._monthly_logs:
            self._monthly_logs[key] = MonthlyLog(year, month)
        return self._monthly_logs[key]

    # --- Ajout d'entrées --------------------------------------------------
    def _register(self, entry: Entry, log: BaseLog) -> None:
        """Ajoute l'entrée au log et met à jour l'index."""
        log.add(entry)
        self._index[entry.id] = log
        logger.info("Ajout %r dans %s", entry, log.title)

    def add_task(
        self,
        name: str,
        description: str = "",
        day: Optional[date] = None,
        signifier: Optional[Signifier] = None,
    ) -> Task:
        """Ajoute une tâche au Daily Log de ``day`` (défaut : aujourd'hui)."""
        task = Task(name, description, day, signifier)
        self._register(task, self.daily_log(task.log_date))
        return task

    def add_event(
        self,
        name: str,
        event_date: date,
        event_time: Optional[time] = None,
        description: str = "",
    ) -> Event:
        """Ajoute un événement au Daily Log de sa date."""
        event = Event(name, event_date, event_time, description)
        self._register(event, self.daily_log(event_date))
        return event

    def add_note(
        self, name: str, description: str = "", day: Optional[date] = None
    ) -> Note:
        """Ajoute une note au Daily Log de ``day``."""
        note = Note(name, description, day)
        self._register(note, self.daily_log(note.log_date))
        return note

    # --- Recherche et actions ---------------------------------------------
    def get_entry(self, entry_id: str) -> Entry:
        """Retourne l'entrée d'identifiant ``entry_id``."""
        try:
            return self._index[entry_id].get(entry_id)
        except KeyError:
            logger.error("Entrée introuvable : %s", entry_id)
            raise EntryNotFoundError(entry_id) from None

    def get_task(self, entry_id: str) -> Task:
        """Comme get_entry, mais vérifie qu'il s'agit d'une tâche."""
        entry = self.get_entry(entry_id)
        if not isinstance(entry, Task):
            raise InvalidTransitionError(
                f"{entry!r} n'est pas une tâche."
            )
        return entry

    def complete_task(self, entry_id: str) -> None:
        """Marque la tâche ``entry_id`` comme terminée."""
        self.get_task(entry_id).complete()
        logger.info("Tâche terminée : %s", entry_id)

    def delete_entry(self, entry_id: str) -> Entry:
        """Supprime définitivement une entrée et la retourne."""
        if entry_id not in self._index:
            logger.error("Suppression impossible, introuvable : %s", entry_id)
            raise EntryNotFoundError(entry_id)
        entry = self._index.pop(entry_id).remove(entry_id)
        logger.info("Suppression %r", entry)
        return entry

    def pending_tasks(self) -> list[Task]:
        """Retourne toutes les tâches à faire, tous logs confondus."""
        return [t for log in self._daily_logs.values()
                for t in log.pending_tasks()]

    # --- Niveau 2 : à vous de jouer ---------------------------------------
    def migrate_task(self, entry_id: str, target_day: date) -> Task:
        """Migre une tâche vers le Daily Log de ``target_day``.

        Idée : marquer l'ancienne en MIGRATED, créer une nouvelle Task
        (même nom, même description, ``origin_id=ancienne.id``) dans le
        log cible, et la retourner.

        Questions à trancher en binôme :
          - peut-on migrer vers une date passée ? vers le même jour ?
          - que faire du signifiant ?
        """
        raise NotImplementedError  # TODO (niveau 2)

    def migrate_day(self, source: date, target: date) -> list[Task]:
        """Migre toutes les tâches TODO du jour ``source`` vers ``target``."""
        raise NotImplementedError  # TODO (niveau 2)

    # TODO (niveau 2) : migrate_month(year, month)
    # TODO (niveau 3) : schedule_task, collections, save/load (storage.py)
