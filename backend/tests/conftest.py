"""Shared pytest fixtures.

`client` builds a TestClient with the app pointed at the fixture content dir and a
throwaway sqlite progress db, so endpoint tests never touch real content/progress.
"""
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

FIXTURE_CONTENT = Path(__file__).parent / "fixtures" / "content"


@pytest.fixture
def client(tmp_path, monkeypatch):
    from app import deps

    deps.configure(content_dir=FIXTURE_CONTENT, progress_db=tmp_path / "p.db")
    from app.main import app

    with TestClient(app) as c:
        yield c
