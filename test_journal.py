"""Tests de la classe Journal."""

from datetime import date

import pytest

from bujo import (EntryNotFoundError, InvalidTransitionError, Journal,
                  TaskState)


@pytest.fixture
def journal():
    """Journal vide réutilisé par les tests."""
    return Journal()


def test_add_task_goes_to_today(journal):
    """Une tâche sans date va dans le log du jour."""
    task = journal.add_task("Courses")
    assert task.id in journal.daily_log()


def test_complete_task(journal):
    """complete_task termine la tâche et la retire des tâches en cours."""
    task = journal.add_task("Courses")
    journal.complete_task(task.id)
    assert task.state is TaskState.DONE
    assert journal.pending_tasks() == []


def test_delete_entry(journal):
    """Une entrée supprimée n'est plus trouvable."""
    task = journal.add_task("Courses")
    journal.delete_entry(task.id)
    with pytest.raises(EntryNotFoundError):
        journal.get_entry(task.id)


def test_delete_unknown_raises(journal):
    """Supprimer un id inconnu lève EntryNotFoundError."""
    with pytest.raises(EntryNotFoundError):
        journal.delete_entry("inexistant")


def test_cannot_complete_a_note(journal):
    """On ne peut pas terminer une note."""
    note = journal.add_note("Il pleut")
    with pytest.raises(InvalidTransitionError):
        journal.complete_task(note.id)


def test_event_goes_to_its_day(journal):
    """Un événement est rangé dans le log de sa date."""
    day = date(2026, 12, 16)
    ev = journal.add_event("Rendu projet", day)
    assert ev.id in journal.daily_log(day)


@pytest.mark.skip(reason="TODO niveau 2 : implémenter migrate_task")
def test_migrate_task(journal):
    """La migration crée une nouvelle tâche liée à l'ancienne."""
    old = journal.add_task("Lire", day=date(2026, 11, 23))
    new = journal.migrate_task(old.id, date(2026, 11, 24))
    assert old.state is TaskState.MIGRATED
    assert new.state is TaskState.TODO
    assert new.origin_id == old.id
    assert new.id != old.id
