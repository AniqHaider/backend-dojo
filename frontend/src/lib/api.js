const BASE = "http://localhost:4001";

async function get(path) {
  const r = await fetch(BASE + path);
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

async function post(path, body) {
  const r = await fetch(BASE + path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!r.ok) throw new Error(`${path} -> ${r.status}`);
  return r.json();
}

export const api = {
  getChapters: () => get("/chapters"),
  getChapter: (id) => get(`/chapters/${id}`),
  getExercise: (id) => get(`/exercises/${id}`),
  runExercise: (id, code) => post(`/exercises/${id}/run`, { code }),
  getProgress: () => get("/progress"),
  getDiagram: () => get("/diagram-state"),
  chat: (question, mode, currentExerciseId, model) =>
    post("/chat", { question, mode, current_exercise_id: currentExerciseId, model }),
};
