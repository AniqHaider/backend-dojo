"""Dependency wiring.

Holds the singletons (ContentLoader, ProgressStore) the routes use. `configure()`
lets tests point them at fixtures + a temp db. Defaults come from config.py.
"""
from __future__ import annotations

from pathlib import Path

from . import config
from .content_loader import ContentLoader
from .progress.store import ProgressStore

_content_dir: Path = config.CONTENT_DIR
_progress_db: Path = config.PROGRESS_DB
_loader: ContentLoader | None = None
_store: ProgressStore | None = None


def configure(*, content_dir: Path | None = None,
              progress_db: Path | None = None) -> None:
    global _content_dir, _progress_db, _loader, _store
    if content_dir is not None:
        _content_dir = Path(content_dir)
    if progress_db is not None:
        _progress_db = Path(progress_db)
    _loader = None
    _store = None


def get_loader() -> ContentLoader:
    global _loader
    if _loader is None:
        _loader = ContentLoader(_content_dir)
    return _loader


def get_store() -> ProgressStore:
    global _store
    if _store is None:
        _store = ProgressStore(_progress_db)
        _store.init_schema()
    return _store
