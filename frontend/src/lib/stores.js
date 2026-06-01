import { writable } from "svelte/store";
import { api } from "./api.js";

export const chapters = writable([]);
export const progress = writable({ xp: 0, level: 1, current_streak: 0, longest_streak: 0, solved_count: 0, solved_ids: [] });
export const diagram = writable({ components: [], unlocked: [] });

// view: { name: 'dashboard' | 'lesson' | 'exercise', chapterId, exerciseId }
export const view = writable({ name: "dashboard" });

// transient: ids of components that JUST unlocked, for the pop animation
export const justUnlocked = writable([]);

export async function refreshAll() {
  const [chs, prog, dia] = await Promise.all([
    api.getChapters(),
    api.getProgress(),
    api.getDiagram(),
  ]);
  chapters.set(chs);
  progress.set(prog);
  diagram.set(dia);
}

export async function refreshProgressAndDiagram(newComponents = []) {
  const [prog, dia, chs] = await Promise.all([
    api.getProgress(),
    api.getDiagram(),
    api.getChapters(),
  ]);
  progress.set(prog);
  diagram.set(dia);
  chapters.set(chs);
  if (newComponents.length) {
    justUnlocked.set(newComponents);
    setTimeout(() => justUnlocked.set([]), 2200);
  }
}

export function goDashboard() {
  view.set({ name: "dashboard" });
}
export function goLesson(chapterId) {
  view.set({ name: "lesson", chapterId });
}
export function goExercise(chapterId, exerciseId) {
  view.set({ name: "exercise", chapterId, exerciseId });
}
