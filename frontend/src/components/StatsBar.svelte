<script>
  import { progress } from "../lib/stores.js";
  import { goDashboard } from "../lib/stores.js";

  // XP needed for next level uses the same curve as the backend: 100 * n*(n-1)/2
  const threshold = (lvl) => (100 * (lvl - 1) * lvl) / 2;
  let cur = $derived(threshold($progress.level));
  let next = $derived(threshold($progress.level + 1));
  let pct = $derived(Math.min(100, Math.round((($progress.xp - cur) / (next - cur)) * 100)));
</script>

<header class="bar">
  <button class="brand" onclick={goDashboard}>
    <span class="logo">⛩️</span> Backend&nbsp;Dojo
  </button>

  <div class="stats">
    <div class="stat level">
      <span class="ring">Lv {$progress.level}</span>
      <div class="xpwrap">
        <div class="xpbar"><div class="xpfill" style="width:{pct}%"></div></div>
        <span class="xptext">{$progress.xp} XP</span>
      </div>
    </div>
    <div class="stat streak" title="Day streak">
      🔥 <b>{$progress.current_streak}</b>
    </div>
    <div class="stat solved" title="Exercises solved">
      ✅ <b>{$progress.solved_count}</b>
    </div>
  </div>
</header>

<style>
  .bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 22px; background: #11161f; border-bottom: 1px solid #1f2735;
    position: sticky; top: 0; z-index: 20;
  }
  .brand {
    background: none; border: none; color: #e8eef6; font-size: 18px; font-weight: 800;
    cursor: pointer; letter-spacing: -0.3px; display: flex; align-items: center; gap: 8px;
  }
  .logo { font-size: 22px; }
  .stats { display: flex; align-items: center; gap: 18px; }
  .stat { display: flex; align-items: center; gap: 8px; color: #c4d0e0; font-size: 14px; }
  .ring {
    background: linear-gradient(135deg, #2f6df6, #7a3af0); color: #fff; font-weight: 700;
    padding: 4px 10px; border-radius: 20px; font-size: 13px;
  }
  .xpwrap { display: flex; align-items: center; gap: 8px; }
  .xpbar { width: 140px; height: 8px; background: #1f2735; border-radius: 6px; overflow: hidden; }
  .xpfill { height: 100%; background: linear-gradient(90deg, #2f6df6, #58c6ff); transition: width .5s ease; }
  .xptext { font-size: 12px; color: #8aa0bd; }
  .streak b, .solved b { color: #fff; }
</style>
