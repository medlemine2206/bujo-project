# bujo — Bibliothèque Python de Bullet Journal

Bibliothèque pour gérer un Bullet Journal : tâches, événements, notes,
Daily/Monthly Logs, migration des tâches.

Voir [CONCEPT.md](CONCEPT.md) pour le modèle objet et les choix de conception.

## Installation

```bash
conda env create -f environment.yml
conda activate bujo
```

## Utilisation rapide

```python
from datetime import date
from bujo import Journal, Signifier, setup_logging

setup_logging()  # écrit logs/debug.log et logs/errors.log

journal = Journal()
t = journal.add_task("Réviser pytest", signifier=Signifier.PRIORITY)
journal.add_event("Rendu projet", date(2026, 12, 16))
journal.add_note("Penser au README")
journal.complete_task(t.id)

print(journal.daily_log().render())
```

## Lancer les vérifications

```bash
flake8 bujo tests        # PEP 8
pydocstyle bujo          # docstrings
pytest --cov=bujo        # tests + couverture
```

## Structure

```
bujo/
  exceptions.py      exceptions personnalisées
  entries.py         Entry (abstraite), Task, Event, Note
  logs.py            DailyLog, MonthlyLog
  journal.py         classe Journal (API principale)
  logging_config.py  configuration des fichiers de log
tests/               tests pytest
.github/workflows/   pipeline CI
```
