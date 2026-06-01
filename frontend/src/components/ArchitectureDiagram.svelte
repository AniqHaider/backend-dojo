<script>
  import { diagram, justUnlocked } from "../lib/stores.js";

  // Group components into the visual stages of a real backend.
  const APP_LAYER = ["py-runtime", "functions", "data-structures", "ch1-complete-core",
                     "type-system", "async-handler", "request-router"];
  const DB_LAYER = ["postgres-db", "tables", "joins-engine"];

  let byId = $derived(Object.fromEntries(($diagram.components || []).map((c) => [c.id, c])));
  let unlocked = $derived(new Set($diagram.unlocked || []));
  let popping = $derived(new Set($justUnlocked || []));

  const label = (id) => byId[id]?.label || id;
  const isOn = (id) => unlocked.has(id);
  const isPop = (id) => popping.has(id);

  let connOn = $derived(unlocked.has("db-connection"));
  let totalOn = $derived(unlocked.size);
  let total = $derived(($diagram.components || []).filter((c) => !c.always).length);
</script>

<div class="diagram">
  <div class="head">
    <h3>Your TicketPay stack</h3>
    <span class="count">{totalOn} / {total} built</span>
  </div>

  <div class="flow">
    <!-- Client -->
    <div class="node client on" class:pop={false}>
      <div class="icon">🌐</div>
      <div class="lbl">Client</div>
    </div>

    <div class="arrow">→</div>

    <!-- Application server -->
    <div class="card server" class:dim={totalOn === 0}>
      <div class="card-title">⚙️ Application</div>
      <div class="pills">
        {#each APP_LAYER as id}
          <div class="pill" class:on={isOn(id)} class:pop={isPop(id)}>{label(id)}</div>
        {/each}
      </div>
    </div>

    <!-- DB connection edge -->
    <div class="arrow conn" class:on={connOn}>{connOn ? "🔌" : "⋯"}</div>

    <!-- Database -->
    <div class="card db" class:dim={!DB_LAYER.some(isOn)}>
      <div class="card-title">🐘 PostgreSQL</div>
      <div class="pills">
        {#each DB_LAYER as id}
          <div class="pill" class:on={isOn(id)} class:pop={isPop(id)}>{label(id)}</div>
        {/each}
      </div>
    </div>
  </div>

  {#if totalOn === 0}
    <p class="hint">Solve your first exercise to start building your backend →</p>
  {/if}
</div>

<style>
  .diagram { background: #11161f; border: 1px solid #1f2735; border-radius: 16px; padding: 20px; }
  .head { display: flex; align-items: baseline; justify-content: space-between; margin-bottom: 16px; }
  .head h3 { margin: 0; color: #e8eef6; font-size: 16px; }
  .count { color: #8aa0bd; font-size: 13px; font-weight: 600; }
  .flow { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
  .arrow { color: #4a5a72; font-size: 22px; }
  .arrow.conn.on { color: #58c6ff; }
  .node {
    display: flex; flex-direction: column; align-items: center; gap: 4px;
    padding: 14px 18px; border-radius: 12px; background: #161d29; border: 1px solid #232d3e;
  }
  .node .icon { font-size: 26px; }
  .node .lbl { font-size: 12px; color: #c4d0e0; }
  .card {
    flex: 1; min-width: 180px; background: #141b26; border: 1px solid #232d3e;
    border-radius: 14px; padding: 14px; transition: opacity .4s, border-color .4s;
  }
  .card.dim { opacity: 0.45; }
  .card-title { font-size: 13px; font-weight: 700; color: #aebfd6; margin-bottom: 10px; }
  .pills { display: flex; flex-direction: column; gap: 7px; }
  .pill {
    font-size: 12.5px; padding: 7px 11px; border-radius: 8px;
    background: #0f141d; color: #5b6b82; border: 1px dashed #2a3344;
    transition: all .45s ease;
  }
  .pill.on {
    background: linear-gradient(135deg, #14304f, #163a2e);
    color: #eaf2ff; border: 1px solid #2f6df6;
    box-shadow: 0 0 0 1px rgba(47,109,246,0.25);
  }
  .pill.pop { animation: pop 1.1s ease; }
  @keyframes pop {
    0% { transform: scale(0.9); box-shadow: 0 0 0 0 rgba(88,198,255,0.7); }
    40% { transform: scale(1.06); box-shadow: 0 0 0 10px rgba(88,198,255,0); }
    100% { transform: scale(1); }
  }
  .hint { color: #6b7d96; font-size: 13px; margin: 16px 0 0; }
</style>
