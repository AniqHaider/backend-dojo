<script>
  import { goExercise } from "../lib/stores.js";
  let { ex, chapterId } = $props();
</script>

<button class="callout" class:solved={ex.solved} onclick={() => goExercise(chapterId, ex.id)}>
  <span class="icon">{ex.solved ? "✅" : "🎯"}</span>
  <span class="body">
    <span class="kicker">{ex.solved ? "Solved — revisit" : "Ready to try"}</span>
    <span class="title">{ex.title}</span>
  </span>
  <span class="meta">
    <span class="badge">{ex.type} · {ex.xp} XP</span>
    <span class="cta">{ex.solved ? "Open" : "Try it"} →</span>
  </span>
</button>

<style>
  .callout {
    width: 100%; display: flex; align-items: center; gap: 14px; text-align: left;
    background: linear-gradient(135deg, #14213a, #131a27);
    border: 1px solid #2f6df6; border-radius: 14px;
    padding: 14px 16px; margin: 18px 0; cursor: pointer;
    transition: transform .1s, box-shadow .2s, border-color .2s;
    box-shadow: 0 0 0 1px rgba(47,109,246,0.12);
  }
  .callout:hover { transform: translateY(-1px); box-shadow: 0 6px 22px rgba(47,109,246,0.25); }
  .callout.solved { border-color: #1c7a55; background: linear-gradient(135deg, #14271f, #131c19); box-shadow: none; }
  .icon { font-size: 22px; flex-shrink: 0; }
  .body { display: flex; flex-direction: column; gap: 2px; flex: 1; min-width: 0; }
  .kicker { font-size: 11px; font-weight: 700; letter-spacing: 0.04em; text-transform: uppercase; color: #6ea8ff; }
  .callout.solved .kicker { color: #58c69a; }
  .title { font-size: 15px; font-weight: 600; color: #eef4fb; }
  .meta { display: flex; flex-direction: column; align-items: flex-end; gap: 6px; flex-shrink: 0; }
  .badge { background: #0f141d; border: 1px solid #232d3e; color: #8aa0bd; font-size: 11px; padding: 3px 8px; border-radius: 14px; white-space: nowrap; }
  .cta { color: #9cc4ff; font-size: 13px; font-weight: 700; white-space: nowrap; }
  .callout.solved .cta { color: #74d6a4; }
</style>
