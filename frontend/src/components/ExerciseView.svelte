<script>
  import { api } from "../lib/api.js";
  import { marked } from "marked";
  import { view, chapters, goLesson, goExercise, refreshProgressAndDiagram } from "../lib/stores.js";
  import CodeEditor from "./CodeEditor.svelte";
  import ResultsPanel from "./ResultsPanel.svelte";

  let exercise = $state(null);
  let code = $state("");
  let result = $state(null);
  let running = $state(false);
  let error = $state(null);
  let loadedId = $state(null);
  let selectedChoice = $state(null); // for quiz exercises
  let isQuiz = $derived(exercise?.type === "quiz");

  // Prev/Next within the chapter, derived from the chapter's exercise order.
  let chapter = $derived($chapters.find((c) => c.id === $view.chapterId));
  let ids = $derived(chapter?.exercise_ids || []);
  let idx = $derived(ids.indexOf($view.exerciseId));
  let prevId = $derived(idx > 0 ? ids[idx - 1] : null);
  let nextId = $derived(idx >= 0 && idx < ids.length - 1 ? ids[idx + 1] : null);
  let isSolved = $derived(Boolean(result?.all_passed) || Boolean(exercise?.solved));

  async function load(id) {
    exercise = null; result = null; error = null; loadedId = id; selectedChoice = null;
    try {
      const ex = await api.getExercise(id);
      exercise = ex;
      code = ex.best_code || ex.starter_code || "";
      if (ex.type === "quiz" && ex.best_code != null && ex.best_code !== "") {
        selectedChoice = Number(ex.best_code);
      }
    } catch (e) { error = e.message; }
  }

  $effect(() => {
    if ($view.name === "exercise" && $view.exerciseId !== loadedId) load($view.exerciseId);
  });

  async function run() {
    running = true; result = null;
    const submission = isQuiz ? String(selectedChoice) : code;
    try {
      result = await api.runExercise(exercise.id, submission);
      await refreshProgressAndDiagram(result.new_components || []);
    } catch (e) {
      result = { all_passed: false, error_category: "network", detail: e.message };
    } finally { running = false; }
  }
</script>

<div class="exercise">
  <button class="back" onclick={() => goLesson($view.chapterId)}>
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M10 3.5 5.5 8l4.5 4.5" stroke="currentColor" stroke-width="1.6"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    Back to chapter
  </button>

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

    {#if isQuiz}
      <div class="options">
        {#each exercise.options as opt, i}
          <button class="option" class:sel={selectedChoice === i}
                  onclick={() => (selectedChoice = i)}>
            <span class="optmark">{String.fromCharCode(65 + i)}</span>
            <span class="opttext">{opt}</span>
          </button>
        {/each}
      </div>
    {:else}
      <CodeEditor {code} language={exercise.type === "sql" ? "sql" : "python"}
                  onChange={(v) => (code = v)} />
    {/if}

    <div class="actions">
      <button class="run" onclick={run} disabled={running || (isQuiz && selectedChoice === null)}>
        {running ? "Checking…" : isQuiz ? "✓ Submit answer" : "▶ Run"}
      </button>
      {#if exercise.hints?.length}
        <details class="hints">
          <summary>💡 Hints ({exercise.hints.length})</summary>
          <ul>{#each exercise.hints as h}<li>{h}</li>{/each}</ul>
        </details>
      {/if}
    </div>

    <ResultsPanel {result} />

    <nav class="exnav">
      <button class="navbtn" disabled={!prevId}
              onclick={() => prevId && goExercise($view.chapterId, prevId)}>
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M10 3.5 5.5 8l4.5 4.5" stroke="currentColor" stroke-width="1.6"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        Previous
      </button>

      <span class="exnav-count">{idx >= 0 ? idx + 1 : "–"} / {ids.length}</span>

      <button class="navbtn next" class:ready={isSolved} disabled={!nextId}
              onclick={() => nextId && goExercise($view.chapterId, nextId)}>
        Next
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M6 3.5 10.5 8 6 12.5" stroke="currentColor" stroke-width="1.6"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </button>
    </nav>
  {/if}
</div>

<style>
  .exercise { max-width: 820px; }
  .back {
    display: inline-flex; align-items: center; gap: 5px;
    background: none; border: none; color: #6ea8ff; cursor: pointer; font-size: 14px;
    margin-bottom: 10px; padding: 4px 6px 4px 0; border-radius: 7px;
  }
  .back:hover { color: #9cc4ff; }
  .back svg { display: block; }
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

  .options { display: flex; flex-direction: column; gap: 10px; }
  .option {
    display: flex; align-items: center; gap: 12px; text-align: left; width: 100%;
    background: #11161f; border: 1px solid #232d3e; color: #d6e2f2;
    padding: 13px 15px; border-radius: 11px; cursor: pointer; font-size: 14.5px; line-height: 1.4;
    transition: border-color .15s, background .15s;
  }
  .option:hover { border-color: #3a4b66; }
  .option.sel { border-color: #2f6df6; background: #14213a; box-shadow: 0 0 0 2px rgba(47,109,246,0.2); }
  .optmark {
    flex-shrink: 0; width: 26px; height: 26px; border-radius: 50%;
    display: grid; place-items: center; background: #1c2536; color: #8aa0bd;
    font-weight: 700; font-size: 13px;
  }
  .option.sel .optmark { background: #2f6df6; color: #fff; }
  .opttext { flex: 1; }

  .exnav {
    display: flex; align-items: center; justify-content: space-between;
    margin-top: 22px; padding-top: 16px; border-top: 1px solid #1f2735;
  }
  .exnav-count { color: #6b7d96; font-size: 13px; font-weight: 600; }
  .navbtn {
    display: inline-flex; align-items: center; gap: 6px;
    background: #161d29; border: 1px solid #232d3e; color: #c4d0e0;
    padding: 9px 15px; border-radius: 10px; cursor: pointer; font-size: 14px; font-weight: 600;
  }
  .navbtn:hover:not(:disabled) { border-color: #2f6df6; color: #eef4fb; }
  .navbtn:disabled { opacity: 0.35; cursor: default; }
  .navbtn svg { display: block; }
  /* highlight Next once the current exercise is solved */
  .navbtn.next.ready {
    background: linear-gradient(135deg, #2f6df6, #1a52d0); border-color: #2f6df6; color: #fff;
    box-shadow: 0 0 0 3px rgba(47,109,246,0.18);
  }
</style>
