<script>
  let { result } = $props();
  // result: { all_passed, results?|rows?, error_category, detail, awarded_xp, new_components }
  let tests = $derived(result?.results || null);
  let rows = $derived(result?.rows || null);
</script>

{#if result}
  <div class="panel" class:ok={result.all_passed} class:bad={!result.all_passed}>
    <div class="status">
      {#if result.all_passed}
        🎉 Passed! {result.awarded_xp > 0 ? `+${result.awarded_xp} XP` : "(already solved)"}
      {:else}
        ❌ Not yet — <span class="cat">{result.error_category}</span>
      {/if}
    </div>

    {#if !result.all_passed && result.detail}
      <pre class="detail">{result.detail}</pre>
    {/if}

    {#if tests}
      <ul class="tests">
        {#each tests as t}
          <li class:pass={t.passed}>
            <code>{t.call}</code>
            {#if !t.passed}
              → expected <code>{t.expected}</code>, got <code>{t.got ?? "—"}</code>
              {#if t.error}<span class="terr">({t.error})</span>{/if}
            {/if}
          </li>
        {/each}
      </ul>
    {/if}

    {#if rows && rows.length}
      <div class="rows">
        <table>
          <thead><tr>{#each Object.keys(rows[0]) as k}<th>{k}</th>{/each}</tr></thead>
          <tbody>
            {#each rows as r}<tr>{#each Object.values(r) as v}<td>{v}</td>{/each}</tr>{/each}
          </tbody>
        </table>
      </div>
    {/if}

    {#if result.new_components?.length}
      <div class="unlock">🧩 Unlocked: {result.new_components.join(", ")}</div>
    {/if}
  </div>
{/if}

<style>
  .panel { border-radius: 12px; padding: 14px; margin-top: 14px; border: 1px solid #232d3e; background: #11161f; }
  .panel.ok { border-color: #1c7a55; }
  .panel.bad { border-color: #7a2f2f; }
  .status { font-weight: 700; color: #eef4fb; font-size: 14px; }
  .cat { color: #ff9d9d; }
  .detail { background: #0e131c; border: 1px solid #2a3344; padding: 10px; border-radius: 8px; color: #ffc9c9; font-size: 12.5px; white-space: pre-wrap; margin: 10px 0 0; }
  .tests { list-style: none; padding: 0; margin: 10px 0 0; }
  .tests li { font-size: 12.5px; color: #ff9d9d; padding: 3px 0; }
  .tests li.pass { color: #74d6a4; }
  .tests code { background: #0e131c; padding: 1px 5px; border-radius: 4px; color: #8fd0ff; }
  .terr { color: #ffb38a; }
  .rows { margin-top: 10px; overflow-x: auto; }
  table { border-collapse: collapse; font-size: 12.5px; }
  th, td { border: 1px solid #232d3e; padding: 5px 10px; color: #cfdbec; text-align: left; }
  th { background: #14304f; color: #eaf2ff; }
  .unlock { margin-top: 12px; color: #58c6ff; font-weight: 600; font-size: 13px; }
</style>
