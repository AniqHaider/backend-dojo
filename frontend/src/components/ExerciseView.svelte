<script>
  import { api } from "../lib/api.js";
  import { marked } from "marked";
  import { view, goLesson, refreshProgressAndDiagram } from "../lib/stores.js";
  import CodeEditor from "./CodeEditor.svelte";
  import ResultsPanel from "./ResultsPanel.svelte";

  let exercise = $state(null);
  let code = $state("");
  let result = $state(null);
  let running = $state(false);
  let error = $state(null);
  let loadedId = $state(null);

  async function load(id) {
    exercise = null; result = null; error = null; loadedId = id;
    try {
      const ex = await api.getExercise(id);
      exercise = ex;
      code = ex.best_code || ex.starter_code || "";
    } catch (e) { error = e.message; }
  }

  $effect(() => {
    if ($view.name === "exercise" && $view.exerciseId !== loadedId) load($view.exerciseId);
  });

  async function run() {
    running = true; result = null;
    try {
      result = await api.runExercise(exercise.id, code);
      await refreshProgressAndDiagram(result.new_components || []);
    } catch (e) {
      result = { all_passed: false, error_category: "network", detail: e.message };
    } finally { running = false; }
  }
</script>

<div class="exercise">
  <button class="back" onclick={() => goLesson($view.chapterId)}>← Back to chapter</button>

  {#if error}
    <p class="err">Couldn't load exercise: {error}</p>
  {:else if !exercise}
    <p class="loading">Loading…</p>
  {:else}
    <div class="head">
      <h1>{exercise.title}</h1>
      <span class="badge">{exercise.type} · {exercise.xp} XP</span>
    </div>

    <div class="prompt">{@html marked.parse(exercise.prompt_md || "")}</div>

    <CodeEditor {code} language={exercise.type === "sql" ? "sql" : "python"}
                onChange={(v) => (code = v)} />

    <div class="actions">
      <button class="run" onclick={run} disabled={running}>
        {running ? "Running…" : "▶ Run"}
      </button>
      {#if exercise.hints?.length}
        <details class="hints">
          <summary>💡 Hints ({exercise.hints.length})</summary>
          <ul>{#each exercise.hints as h}<li>{h}</li>{/each}</ul>
        </details>
      {/if}
    </div>

    <ResultsPanel {result} />
  {/if}
</div>

<style>
  .exercise { max-width: 820px; }
  .back { background: none; border: none; color: #6ea8ff; cursor: pointer; font-size: 14px; margin-bottom: 10px; }
  .head { display: flex; align-items: center; gap: 12px; }
  h1 { color: #eef4fb; font-size: 22px; margin: 4px 0 0; }
  .badge { background: #161d29; border: 1px solid #232d3e; color: #8aa0bd; font-size: 12px; padding: 3px 9px; border-radius: 20px; }
  .prompt { color: #c8d4e4; line-height: 1.6; font-size: 15px; margin: 12px 0 14px; }
  .prompt :global(code) { background: #161d29; padding: 1px 6px; border-radius: 5px; color: #8fd0ff; font-size: 13px; }
  .actions { display: flex; align-items: center; gap: 16px; margin-top: 14px; }
  .run {
    background: linear-gradient(135deg, #2f6df6, #1a52d0); color: #fff; border: none;
    padding: 10px 22px; border-radius: 10px; font-weight: 700; cursor: pointer; font-size: 14px;
  }
  .run:disabled { opacity: 0.6; cursor: default; }
  .hints { color: #aebfd6; font-size: 13px; }
  .hints summary { cursor: pointer; }
  .hints ul { margin: 6px 0 0; color: #8aa0bd; }
  .loading, .err { color: #8aa0bd; }
</style>
