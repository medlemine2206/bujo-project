"""Tests des entrées et du cycle de vie des tâches."""

from datetime import date, time

import pytest

from bujo import (EmptyNameError, Event, InvalidTransitionError, Note,
                  Signifier, Task, TaskState)


def test_task_starts_todo():
    """Une tâche neuve est à l'état TODO avec le symbole •."""
    task = Task("Réviser")
    assert task.state is TaskState.TODO
    assert task.render() == "• Réviser"


def test_ids_are_unique_even_with_same_name():
    """Deux tâches de même nom ont des id différents."""
    assert Task("A").id != Task("A").id


@pytest.mark.parametrize("bad_name", ["", "   ", None])
def test_empty_name_raises(bad_name):
    """Un nom vide est refusé."""
    with pytest.raises(EmptyNameError):
        Task(bad_name)


def test_complete():
    """complete() passe la tâche en DONE."""
    task = Task("A")
    task.complete()
    assert task.state is TaskState.DONE
    assert task.render() == "× A"


def test_cannot_complete_cancelled_task():
    """Terminer une tâche abandonnée est interdit."""
    task = Task("A")
    task.cancel()
    with pytest.raises(InvalidTransitionError):
        task.complete()


def test_cancelled_is_struck_through():
    """Une tâche abandonnée s'affiche barrée."""
    task = Task("A")
    task.cancel()
    assert task.render() == "~~A~~"


def test_signifier_prefix():
    """Le signifiant apparaît devant le symbole."""
    assert Task("A", signifier=Signifier.PRIORITY).render() == "* • A"


def test_event_and_note_symbols():
    """Événement ○ (avec heure) et note –."""
    ev = Event("Partiel", date(2026, 12, 10), time(9, 0))
    assert ev.render() == "○ 09:00 Partiel"
    assert Note("Idée").render() == "– Idée"

# TODO : tester schedule(), mark_migrated(), to_dict(), toutes les
# transitions interdites (utiliser pytest.mark.parametrize !)
