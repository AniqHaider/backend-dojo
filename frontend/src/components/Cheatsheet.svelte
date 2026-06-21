<script>
  import { marked } from "marked";
  import { api } from "../lib/api.js";

  let { open = false, onClose } = $props();

  let loaded = $state(false);
  let error = $state(null);
  let intro = $state("");
  let sections = $state([]); // [{ title, body }]
  let query = $state("");

  async function ensureLoaded() {
    if (loaded || error) return;
    try {
      const { markdown } = await api.getReference("python-cheatsheet");
      const parts = markdown.split(/\n## /);
      intro = parts[0].replace(/^# .*\n/, "").trim();
      sections = parts.slice(1).map((chunk) => {
        const nl = chunk.indexOf("\n");
        return { title: chunk.slice(0, nl).trim(), body: chunk.slice(nl + 1).trim() };
      });
      loaded = true;
    } catch (e) {
      error = e.message;
    }
  }

  // load on first open
  $effect(() => { if (open) ensureLoaded(); });

  let filtered = $derived(
    query.trim()
      ? sections.filter((s) =>
          (s.title + " " + s.body).toLowerCase().includes(query.trim().toLowerCase()))
      : sections
  );
</script>

<svelte:window onkeydown={(e) => { if (open && e.key === "Escape") onClose(); }} />

{#if open}
  <!-- svelte-ignore a11y_click_events_have_key_events -->
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div class="overlay" onclick={onClose} role="presentation">
    <div class="sheet" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-label="Python cheatsheet">
      <div class="head">
        <h2>📘 Python syntax cheatsheet</h2>
        <button class="close" onclick={onClose} aria-label="Close">✕</button>
      </div>

      <input class="search" placeholder="Filter… (e.g. dict, loop, f-string)"
             bind:value={query} />

      <div class="content">
        {#if error}
          <p class="err">Couldn't load cheatsheet: {error}</p>
        {:else if !loaded}
          <p class="dim">Loading…</p>
        {:else}
          {#if !query.trim() && intro}
            <div class="intro md">{@html marked.parse(intro)}</div>
          {/if}
          {#if filtered.length === 0}
            <p class="dim">No matches for “{query}”.</p>
          {/if}
          {#each filtered as s (s.title)}
            <details open={Boolean(query.trim())}>
              <summary>{s.title}</summary>
              <div class="md">{@html marked.parse(s.body)}</div>
            </details>
          {/each}
        {/if}
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay {
    position: fixed; inset: 0; z-index: 60; background: rgba(4, 8, 14, 0.62);
    display: flex; justify-content: flex-end;
  }
  .sheet {
    width: min(560px, 92vw); height: 100%; background: #0f141d;
    border-left: 1px solid #2a3344; display: flex; flex-direction: column;
    box-shadow: -16px 0 48px rgba(0,0,0,0.5); animation: slidein .18s ease;
  }
  @keyframes slidein { from { transform: translateX(24px); opacity: 0.4; } to { transform: none; opacity: 1; } }
  .head { display: flex; align-items: center; justify-content: space-between; padding: 16px 18px; border-bottom: 1px solid #1f2735; }
  .head h2 { margin: 0; font-size: 16px; color: #eef4fb; }
  .close { background: none; border: none; color: #8aa0bd; font-size: 16px; cursor: pointer; padding: 4px 8px; border-radius: 7px; }
  .close:hover { color: #fff; background: #1c2536; }
  .search {
    margin: 12px 18px 4px; padding: 9px 12px; background: #161d29; border: 1px solid #232d3e;
    border-radius: 9px; color: #e8eef6; font-size: 13px; font-family: inherit;
  }
  .search:focus { outline: none; border-color: #2f6df6; }
  .content { overflow-y: auto; padding: 10px 18px 28px; }
  .intro { color: #aebfd6; font-size: 13px; margin-bottom: 8px; }
  details { border-bottom: 1px solid #1a2230; padding: 4px 0; }
  summary { cursor: pointer; color: #cfe0f5; font-weight: 700; font-size: 14px; padding: 8px 0; list-style: none; }
  summary::-webkit-details-marker { display: none; }
  summary::before { content: "▸ "; color: #4a5a72; }
  details[open] summary::before { content: "▾ "; }
  .dim { color: #6b7d96; font-size: 13px; }
  .err { color: #ff9d9d; font-size: 13px; }

  .md { color: #c8d4e4; font-size: 13.5px; line-height: 1.55; }
  .md :global(p) { margin: 6px 0; }
  .md :global(code) { background: #161d29; padding: 1px 5px; border-radius: 4px; color: #8fd0ff; font-size: 12.5px; }
  .md :global(pre) { background: #0b0f16; border: 1px solid #1f2735; padding: 11px 13px; border-radius: 9px; overflow-x: auto; margin: 8px 0; }
  .md :global(pre code) { background: none; padding: 0; color: #d6e2f2; font-size: 12.5px; }
  .md :global(strong) { color: #eef4fb; }
</style>
