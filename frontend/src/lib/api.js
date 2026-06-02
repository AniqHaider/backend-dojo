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

  // Streams the tutor's answer. Calls onChunk(fullTextSoFar) as text arrives.
  // Returns the complete answer string.
  chatStream: async (question, mode, currentExerciseId, model, onChunk) => {
    const r = await fetch(BASE + "/chat/stream", {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({ question, mode, current_exercise_id: currentExerciseId, model }),
    });
    if (!r.ok || !r.body) throw new Error(`/chat/stream -> ${r.status}`);
    const reader = r.body.getReader();
    const decoder = new TextDecoder();
    let full = "";
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      full += decoder.decode(value, { stream: true });
      if (onChunk) onChunk(full);
    }
    return full;
  },
};
