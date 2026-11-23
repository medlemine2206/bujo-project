"""Configuration du module logging.

Produit deux fichiers, comme demandé dans le sujet :
  - ``logs/debug.log``  : tout (DEBUG et plus)
  - ``logs/errors.log`` : uniquement ERROR et CRITICAL
"""

import logging
from pathlib import Path

_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"


def setup_logging(log_dir: str | Path = "logs") -> None:
    """Configure les handlers du logger ``bujo``.

    À appeler une fois par l'application qui utilise la bibliothèque
    (une bibliothèque ne doit pas configurer le logging toute seule à
    l'import).
    """
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("bujo")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # évite les doublons si appelé deux fois

    formatter = logging.Formatter(_FORMAT)

    debug_handler = logging.FileHandler(path / "debug.log", encoding="utf-8")
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(formatter)

    error_handler = logging.FileHandler(path / "errors.log", encoding="utf-8")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    logger.addHandler(debug_handler)
    logger.addHandler(error_handler)
