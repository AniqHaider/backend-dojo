from datetime import date

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from . import deps
from .config import FRONTEND_ORIGIN
from .chat import ask_claude, build_context, stream_claude
from .diagram import COMPONENTS
from .grading import process_run


class RunRequest(BaseModel):
    code: str


class ChatRequest(BaseModel):
    question: str
    mode: str = "tutor"
    current_exercise_id: str | None = None
    model: str | None = None

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


@app.post("/exercises/{exercise_id}/run")
def run_exercise(exercise_id: str, req: RunRequest):
    loader = deps.get_loader()
    store = deps.get_store()
    try:
        return process_run(store, loader, exercise_id, req.code,
                           today=date.today().isoformat())
    except KeyError:
        raise HTTPException(status_code=404, detail="exercise not found")


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


def _build_chat_context(req: ChatRequest) -> str:
    loader = deps.get_loader()
    store = deps.get_store()
    current = None
    if req.current_exercise_id:
        try:
            current = loader.get_exercise_public(req.current_exercise_id)
            current["best_code"] = store.get_exercise(req.current_exercise_id).get("best_code")
        except KeyError:
            current = None
    return build_context(
        question=req.question,
        current_exercise=current,
        recent_mistakes=store.recent_mistakes(limit=8),
        solved=sorted(store.solved_ids()),
    )


@app.post("/chat")
def chat(req: ChatRequest):
    context = _build_chat_context(req)
    answer = ask_claude(question=req.question, mode=req.mode,
                        context=context, model=req.model)
    return {"answer": answer}


@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    context = _build_chat_context(req)
    gen = stream_claude(question=req.question, mode=req.mode,
                        context=context, model=req.model)
    return StreamingResponse(gen, media_type="text/plain; charset=utf-8")
