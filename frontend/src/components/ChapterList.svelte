<script>
  import { chapters, goLesson } from "../lib/stores.js";
</script>

<div class="chapters">
  <h2>Chapters</h2>
  {#each $chapters as ch}
    {@const pct = ch.exercise_count ? Math.round((ch.solved_count / ch.exercise_count) * 100) : 0}
    <button class="chapter" onclick={() => goLesson(ch.id)}>
      <div class="ring" style="--pct:{pct}">
        <span>{pct}%</span>
      </div>
      <div class="meta">
        <div class="title">{ch.title}</div>
        <div class="summary">{ch.summary}</div>
        <div class="prog">{ch.solved_count} / {ch.exercise_count} solved</div>
      </div>
      <div class="go">→</div>
    </button>
  {/each}
</div>

<style>
  .chapters h2 { color: #e8eef6; font-size: 17px; margin: 0 0 14px; }
  .chapter {
    width: 100%; display: flex; align-items: center; gap: 16px; text-align: left;
    background: #11161f; border: 1px solid #1f2735; border-radius: 14px;
    padding: 16px; margin-bottom: 12px; cursor: pointer; transition: border-color .2s, transform .1s;
  }
  .chapter:hover { border-color: #2f6df6; transform: translateY(-1px); }
  .ring {
    width: 54px; height: 54px; border-radius: 50%; flex-shrink: 0;
    display: grid; place-items: center; font-size: 12px; font-weight: 700; color: #cfe0f5;
    background: radial-gradient(closest-side, #11161f 70%, transparent 71%),
                conic-gradient(#2f6df6 calc(var(--pct) * 1%), #232d3e 0);
  }
  .meta { flex: 1; }
  .title { color: #eef4fb; font-weight: 700; font-size: 15px; }
  .summary { color: #8aa0bd; font-size: 13px; margin: 3px 0; }
  .prog { color: #6b7d96; font-size: 12px; }
  .go { color: #4a5a72; font-size: 20px; }
</style>
