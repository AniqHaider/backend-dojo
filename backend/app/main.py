from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import FRONTEND_ORIGIN

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
