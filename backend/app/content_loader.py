"""Loads chapter content from disk.

Chapters live as directories under a content root. Each chapter has:
  meta.json        -> {id, title, order, summary, [diagram?]}
  theory.md        -> long-form beginner theory
  exercises/*.json -> one exercise per file (see spec sec 3.2)

The loader is the ONLY place that reads content, and it strips hidden fields
(`tests`, `expected_query_result`) before anything reaches the client.
"""
from __future__ import annotations

import json
from pathlib import Path

HIDDEN_FIELDS = ("tests", "expected_query_result")


class ContentLoader:
    def __init__(self, content_dir: Path | str):
        self.content_dir = Path(content_dir)

    # ---- internal --------------------------------------------------------
    def _chapter_dirs(self) -> list[Path]:
        if not self.content_dir.exists():
            return []
        return sorted(
            d for d in self.content_dir.iterdir()
            if d.is_dir() and (d / "meta.json").exists()
        )

    def _load_meta(self, chapter_dir: Path) -> dict:
        return json.loads((chapter_dir / "meta.json").read_text())

    def _load_exercises(self, chapter_dir: Path) -> list[dict]:
        ex_dir = chapter_dir / "exercises"
        if not ex_dir.exists():
            return []
        files = sorted(ex_dir.glob("*.json"))
        return [json.loads(f.read_text()) for f in files]

    def _find_exercise(self, exercise_id: str) -> dict:
        for ch_dir in self._chapter_dirs():
            for ex in self._load_exercises(ch_dir):
                if ex.get("id") == exercise_id:
                    return ex
        raise KeyError(exercise_id)

    @staticmethod
    def _strip(ex: dict) -> dict:
        return {k: v for k, v in ex.items() if k not in HIDDEN_FIELDS}

    # ---- public API ------------------------------------------------------
    def list_chapters(self) -> list[dict]:
        out = []
        for ch_dir in self._chapter_dirs():
            meta = self._load_meta(ch_dir)
            exercises = self._load_exercises(ch_dir)
            out.append({
                "id": meta["id"],
                "title": meta["title"],
                "order": meta.get("order", 0),
                "summary": meta.get("summary", ""),
                "exercise_count": len(exercises),
                "exercise_ids": [e["id"] for e in exercises],
            })
        out.sort(key=lambda c: c["order"])
        return out

    def get_chapter(self, chapter_id: str) -> dict:
        for ch_dir in self._chapter_dirs():
            meta = self._load_meta(ch_dir)
            if meta["id"] != chapter_id:
                continue
            theory_path = ch_dir / "theory.md"
            theory = theory_path.read_text() if theory_path.exists() else ""
            exercises = [self._strip(e) for e in self._load_exercises(ch_dir)]
            return {
                "id": meta["id"],
                "title": meta["title"],
                "summary": meta.get("summary", ""),
                "theory_md": theory,
                "exercises": exercises,
            }
        raise KeyError(chapter_id)

    def get_exercise_public(self, exercise_id: str) -> dict:
        return self._strip(self._find_exercise(exercise_id))

    def get_exercise_full(self, exercise_id: str) -> dict:
        return self._find_exercise(exercise_id)
