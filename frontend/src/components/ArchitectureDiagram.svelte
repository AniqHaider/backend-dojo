<script>
  import { diagram, justUnlocked } from "../lib/stores.js";

  const ZONES = [
    { key: "application", title: "⚙️ Application" },
    { key: "data", title: "🐘 Data" },
    { key: "infrastructure", title: "☁️ Infrastructure" },
  ];

  let comps = $derived($diagram.components || []);
  let unlocked = $derived(new Set($diagram.unlocked || []));
  let popping = $derived(new Set($justUnlocked || []));

  let clientComp = $derived(comps.find((c) => c.group === "client"));
  let zones = $derived(
    ZONES.map((z) => ({ ...z, items: comps.filter((c) => c.group === z.key) }))
  );

  let total = $derived(comps.filter((c) => !c.always).length);
  let totalOn = $derived(comps.filter((c) => !c.always && unlocked.has(c.id)).length);

  const isOn = (id) => unlocked.has(id);
  const isPop = (id) => popping.has(id);
</script>

<div class="diagram">
  <div class="head">
    <h3>Your TicketPay stack</h3>
    <span class="count">{totalOn} / {total} built</span>
  </div>

  <div class="flow">
    {#if clientComp}
      <div class="node on"><div class="icon">🌐</div><div class="lbl">Client</div></div>
      <div class="arrow">→</div>
    {/if}

    {#each zones as z, zi}
      <div class="card" class:dim={!z.items.some((c) => isOn(c.id))}>
        <div class="card-title">{z.title}</div>
        <div class="pills">
          {#each z.items as c}
            <div class="pill" class:on={isOn(c.id)} class:pop={isPop(c.id)}>{c.label}</div>
          {/each}
        </div>
      </div>
      {#if zi < zones.length - 1}<div class="arrow">→</div>{/if}
    {/each}
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
  .flow { display: flex; align-items: stretch; gap: 10px; flex-wrap: wrap; }
  .arrow { color: #4a5a72; font-size: 20px; align-self: center; }
  .node {
    display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 4px;
    padding: 14px 16px; border-radius: 12px; background: #161d29; border: 1px solid #232d3e;
  }
  .node .icon { font-size: 24px; }
  .node .lbl { font-size: 12px; color: #c4d0e0; }
  .card {
    flex: 1 1 200px; min-width: 190px; background: #141b26; border: 1px solid #232d3e;
    border-radius: 14px; padding: 14px; transition: opacity .4s, border-color .4s;
  }
  .card.dim { opacity: 0.4; }
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
