<script>
  import { onMount } from "svelte";
  import { marked } from "marked";
  import { api } from "../lib/api.js";
  import { view, goExercise, goDashboard } from "../lib/stores.js";

  let chapter = $state(null);
  let error = $state(null);

  async function load(id) {
    chapter = null; error = null;
    try { chapter = await api.getChapter(id); }
    catch (e) { error = e.message; }
  }

  $effect(() => { if ($view.name === "lesson") load($view.chapterId); });
</script>

<div class="lesson">
  <button class="back" onclick={goDashboard}>
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M10 3.5 5.5 8l4.5 4.5" stroke="currentColor" stroke-width="1.6"
            stroke-linecap="round" stroke-linejoin="round"/>
    </svg>
    Dashboard
  </button>

  {#if error}
    <p class="err">Couldn't load chapter: {error}</p>
  {:else if !chapter}
    <p class="loading">Loading…</p>
  {:else}
    <h1>{chapter.title}</h1>
    <div class="layout">
      <article class="theory">{@html marked.parse(chapter.theory_md || "")}</article>
      <aside class="exlist">
        <h3>Exercises</h3>
        {#each chapter.exercises as ex, i}
          <button class="exitem" class:solved={ex.solved}
                  onclick={() => goExercise(chapter.id, ex.id)}>
            <span class="num">{ex.solved ? "✅" : i + 1}</span>
            <span class="extitle">{ex.title}</span>
            <span class="xp">{ex.xp} XP</span>
          </button>
        {/each}
      </aside>
    </div>
  {/if}
</div>

<style>
  .lesson { max-width: 1100px; }
  .back { display: inline-flex; align-items: center; gap: 5px; background: none; border: none; color: #6ea8ff; cursor: pointer; font-size: 14px; margin-bottom: 10px; padding: 4px 6px 4px 0; }
  .back:hover { color: #9cc4ff; }
  .back svg { display: block; }
  h1 { color: #eef4fb; font-size: 24px; margin: 4px 0 18px; }
  .layout { display: grid; grid-template-columns: 1fr 300px; gap: 24px; align-items: start; }
  .theory { color: #c8d4e4; line-height: 1.7; font-size: 15px; }
  .theory :global(h2) { color: #eef4fb; font-size: 19px; margin: 22px 0 8px; border-bottom: 1px solid #1f2735; padding-bottom: 6px; }
  .theory :global(h3) { color: #dce6f4; font-size: 16px; margin: 18px 0 6px; }
  .theory :global(code) { background: #161d29; padding: 1px 6px; border-radius: 5px; font-size: 13px; color: #8fd0ff; }
  .theory :global(pre) { background: #0e131c; border: 1px solid #1f2735; padding: 14px; border-radius: 10px; overflow-x: auto; }
  .theory :global(pre code) { background: none; color: #d6e2f2; }
  .theory :global(strong) { color: #eef4fb; }
  .theory :global(blockquote) { border-left: 3px solid #2f6df6; margin: 12px 0; padding: 4px 14px; color: #aebfd6; background: #11161f; border-radius: 0 8px 8px 0; }
  .exlist { background: #11161f; border: 1px solid #1f2735; border-radius: 14px; padding: 14px; position: sticky; top: 80px; }
  .exlist h3 { color: #aebfd6; font-size: 14px; margin: 0 0 10px; }
  .exitem {
    width: 100%; display: flex; align-items: center; gap: 10px; text-align: left;
    background: #0f141d; border: 1px solid #1f2735; border-radius: 9px;
    padding: 9px 11px; margin-bottom: 7px; cursor: pointer; color: #c4d0e0; font-size: 13px;
  }
  .exitem:hover { border-color: #2f6df6; }
  .exitem.solved { border-color: #1c7a55; }
  .num { width: 22px; text-align: center; color: #6b7d96; font-weight: 700; }
  .extitle { flex: 1; }
  .xp { color: #6b7d96; font-size: 11px; }
  .loading, .err { color: #8aa0bd; }
</style>
