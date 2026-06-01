from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import deps
from .config import FRONTEND_ORIGIN
from .diagram import COMPONENTS

app = FastAPI(title="Backend Dojo")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/chapters")
def list_chapters():
    loader = deps.get_loader()
    store = deps.get_store()
    solved = store.solved_ids()
    chapters = loader.list_chapters()
    for ch in chapters:
        ids = ch.get("exercise_ids", [])
        ch["solved_count"] = sum(1 for i in ids if i in solved)
    return chapters


@app.get("/chapters/{chapter_id}")
def get_chapter(chapter_id: str):
    loader = deps.get_loader()
    store = deps.get_store()
    try:
        ch = loader.get_chapter(chapter_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="chapter not found")
    solved = store.solved_ids()
    for ex in ch["exercises"]:
        ex["solved"] = ex["id"] in solved
    return ch


@app.get("/exercises/{exercise_id}")
def get_exercise(exercise_id: str):
    loader = deps.get_loader()
    store = deps.get_store()
    try:
        ex = loader.get_exercise_public(exercise_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="exercise not found")
    prog = store.get_exercise(exercise_id)
    ex["solved"] = prog["status"] == "solved"
    ex["best_code"] = prog.get("best_code")
    return ex


@app.get("/progress")
def get_progress():
    store = deps.get_store()
    stats = store.get_stats()
    solved = store.solved_ids()
    stats["solved_ids"] = sorted(solved)
    stats["solved_count"] = len(solved)
    return stats


@app.get("/diagram-state")
def diagram_state():
    store = deps.get_store()
    return {"components": COMPONENTS, "unlocked": store.unlocked_components()}
