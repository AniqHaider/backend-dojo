"""Context-aware chat backed by the local `claude` CLI.

`build_context` and `system_prompt_for` are pure (unit-tested). `ask_claude` spawns
`claude -p ... --append-system-prompt ...` and returns its stdout. The whole point is
that the tutor sees the learner's progress and recent mistakes, so its help is
personal — e.g. "you keep forgetting to `return`".
"""
from __future__ import annotations

import subprocess

CLI_TIMEOUT = 180

TUTOR_PROMPT = (
    "You are a patient backend-engineering tutor for a learner who is a strong "
    "FRONTEND engineer but NEW to backend. Use a Socratic style: give hints, ask "
    "leading questions, and point out the learner's specific past mistakes shown in "
    "the context. DO NOT give the full solution to the current exercise outright; "
    "guide them to it. Be concise and encouraging. Define backend jargon when you use it."
)

EXPLAIN_PROMPT = (
    "You are a clear backend-engineering teacher for a learner who is a strong "
    "FRONTEND engineer but NEW to backend. Explain concepts directly and concretely "
    "with small examples and analogies. Define every backend term you use. Be concise. "
    "It's fine to give direct answers to conceptual questions, but still avoid writing "
    "the complete solution to an active coding exercise unless explicitly asked."
)


def system_prompt_for(mode: str) -> str:
    return EXPLAIN_PROMPT if mode == "explain" else TUTOR_PROMPT


def build_context(*, question: str, current_exercise: dict | None,
                  recent_mistakes: list[dict], solved: list[str]) -> str:
    parts: list[str] = []

    if current_exercise:
        parts.append("## Current exercise")
        parts.append(f"id: {current_exercise.get('id')}")
        parts.append(f"title: {current_exercise.get('title', '')}")
        parts.append(f"prompt: {current_exercise.get('prompt_md', '')}")
        if current_exercise.get("best_code"):
            parts.append("learner's latest submission:\n"
                         f"```\n{current_exercise['best_code']}\n```")

    if solved:
        parts.append("## Exercises already solved")
        parts.append(", ".join(solved))

    if recent_mistakes:
        parts.append("## Learner's recent mistakes (most recent first)")
        for m in recent_mistakes:
            parts.append(
                f"- {m.get('exercise_id')}: {m.get('error_category')}"
                + (f" — {m.get('detail')}" if m.get("detail") else "")
            )

    parts.append("## The learner's question")
    parts.append(question)

    return "\n".join(parts)


def ask_claude(*, question: str, mode: str, context: str,
               model: str | None = None) -> str:
    cmd = ["claude", "-p", context, "--append-system-prompt", system_prompt_for(mode)]
    if model:
        cmd += ["--model", model]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=CLI_TIMEOUT)
    except subprocess.TimeoutExpired:
        return "(The tutor took too long to respond. Please try again.)"
    if proc.returncode != 0:
        return f"(Tutor unavailable: {proc.stderr.strip()[:300]})"
    return proc.stdout.strip()
