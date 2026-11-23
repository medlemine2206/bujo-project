# Concept du projet — Bibliothèque Python « bujo »

## 1. L'idée en une phrase

Un **journal** contient des **logs** (pages datées : jour, mois, futur) et des
**collections** (pages thématiques). Chaque page contient des **entrées**
(tâches, événements, notes). Les tâches ont un **cycle de vie** dont le geste
central est la **migration**.

## 2. Modèle objet

```
                    Entry  (classe abstraite)
        id, name, description, created_at, log_date, signifier
        symbol (abstrait), to_dict(), from_dict()
              ┌───────────┼───────────┐
             Task       Event        Note
           + state     + date       (rien de plus,
           + complete()  + time      ne peut pas être
           + migrate()               migrée ni terminée)
           + schedule()
           + cancel()

    BaseLog (abstraite) ── contient des Entry (dict id -> Entry)
        ├── DailyLog    (une date précise)
        ├── MonthlyLog  (année + mois)
        └── FutureLog   (niveau 3)

    Collection ── page libre nommée (niveau 3)

    Journal ── point d'entrée de l'API
        daily_logs   : dict[date, DailyLog]
        monthly_logs : dict[(année, mois), MonthlyLog]
        collections  : dict[str, Collection]
        index        : où trouver chaque entrée (id -> log)
```

## 3. Cycle de vie d'une tâche (machine à états)

```
                    complete()
        TODO ─────────────────────► DONE
         │  \
         │   \ migrate()            (une copie TODO est créée
         │    └───────────────────► MIGRATED   dans le log cible)
         │
         ├── schedule() ──────────► SCHEDULED  (part dans le Future Log)
         │
         └── cancel() ────────────► CANCELLED
```

Règle : **seule une tâche TODO peut changer d'état.** Toute autre transition
lève `InvalidTransitionError` (ex. terminer une tâche abandonnée).
Une `Note` ou un `Event` qu'on tente de migrer lève aussi une erreur.

### Décision de conception : la migration crée une NOUVELLE tâche

Dans un vrai BuJo, on barre l'ancienne ligne (`>`) et on la réécrit ailleurs.
On reproduit ça : l'ancienne tâche passe en `MIGRATED` (on garde l'historique),
et une nouvelle tâche `TODO` avec un **nouvel id** est créée dans le log cible.
Elle garde un lien `origin_id` vers l'ancienne. C'est pour ça que le sujet
impose un identifiant unique : deux tâches peuvent avoir le même nom.

## 4. Symboles (rapid logging)

| Objet                | Symbole |
|----------------------|---------|
| Task TODO            | `•`     |
| Task DONE            | `×`     |
| Task MIGRATED        | `>`     |
| Task SCHEDULED       | `<`     |
| Task CANCELLED       | `~~nom~~` |
| Event                | `○`     |
| Note                 | `–`     |
| Signifiant PRIORITY  | `*` (préfixe) |
| Signifiant IDEA      | `!` (préfixe) |

Chaque sous-classe sait afficher son propre symbole → **polymorphisme** :
le log fait juste `entry.render()` sans savoir de quel type il s'agit.

## 5. Découpage en modules

| Module                 | Rôle                                   | Niveau |
|------------------------|----------------------------------------|--------|
| `bujo/exceptions.py`   | Exceptions personnalisées              | 1      |
| `bujo/entries.py`      | Entry, Task, Event, Note, enums        | 1      |
| `bujo/logs.py`         | DailyLog, MonthlyLog (FutureLog)       | 1–2    |
| `bujo/journal.py`      | Classe Journal (façade de l'API)       | 1–2    |
| `bujo/logging_config.py` | Config logging (debug.log + errors.log) | 1   |
| `bujo/storage.py`      | Sauvegarde/chargement JSON             | 3      |
| `bujo/export.py`       | Export Markdown                        | 3      |
| `bujo/search.py`       | Recherche multi-critères               | 3      |
| `bujo/cli.py`          | Interface argparse (`bujo add ...`)    | bonus  |

## 6. Ce qui est déjà fait / ce qui reste

**Fourni dans ce squelette (niveau 1 quasi complet) :**
- Hiérarchie Entry/Task/Event/Note avec validation et symboles
- Machine à états de Task (complete, cancel, schedule, mark_migrated)
- DailyLog/MonthlyLog basiques
- Journal : add_task, add_event, add_note, complete_task, delete_entry,
  pending_tasks, get_entry
- Logging vers 2 fichiers, exceptions, premiers tests, CI GitHub Actions

**À vous de réfléchir et coder (marqué `TODO` dans le code) :**
- `Journal.migrate_task()` et `Journal.migrate_day()` / `migrate_month()` (niveau 2)
- Affichage complet d'un log en rapid logging, tri, en-têtes (niveau 2)
- FutureLog, Collection, Index (niveau 3)
- `storage.py` (JSON, **pas de pickle**), `export.py`, `search.py` (niveau 3)
- Compléter les tests → objectif couverture > 90 %
- Sphinx, packaging `pyproject.toml`, déploiement PyPI (bonus)

## 7. Proposition de répartition à deux

| Personne A                          | Personne B                         |
|-------------------------------------|------------------------------------|
| entries.py + tests du cycle de vie  | logs.py + journal.py + leurs tests |
| migration (niveau 2)                | affichage rapid logging (niveau 2) |
| storage.py (JSON)                   | export.py + search.py              |
| CI + flake8/pydocstyle              | Sphinx + README                    |

Travaillez sur des branches (`feature/migration`, `feature/storage`…) et
fusionnez par Pull Request en vous relisant mutuellement.
