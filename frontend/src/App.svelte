<script>
  import { onMount } from "svelte";
  import { view, refreshAll } from "./lib/stores.js";
  import StatsBar from "./components/StatsBar.svelte";
  import ArchitectureDiagram from "./components/ArchitectureDiagram.svelte";
  import ChapterList from "./components/ChapterList.svelte";
  import LessonView from "./components/LessonView.svelte";
  import ExerciseView from "./components/ExerciseView.svelte";
  import ChatPanel from "./components/ChatPanel.svelte";

  let booted = $state(false);
  let bootError = $state(null);

  onMount(async () => {
    try { await refreshAll(); booted = true; }
    catch (e) { bootError = e.message; }
  });
</script>

<StatsBar />

<main>
  {#if bootError}
    <div class="boot err">
      <h2>Can't reach the backend</h2>
      <p>Make sure the API is running on <code>http://localhost:4001</code>.</p>
      <p class="dim">{bootError}</p>
    </div>
  {:else if !booted}
    <div class="boot">Loading your dojo…</div>
  {:else if $view.name === "dashboard"}
    <div class="dashboard">
      <ArchitectureDiagram />
      <ChapterList />
    </div>
  {:else if $view.name === "lesson"}
    <LessonView />
  {:else if $view.name === "exercise"}
    <ExerciseView />
  {/if}
</main>

<ChatPanel />

<style>
  main { padding: 24px; max-width: 1200px; margin: 0 auto; }
  .dashboard { display: flex; flex-direction: column; gap: 22px; }
  .boot { color: #8aa0bd; text-align: center; padding: 80px 20px; }
  .boot.err h2 { color: #ff9d9d; }
  .boot code { background: #161d29; padding: 2px 7px; border-radius: 5px; color: #8fd0ff; }
  .dim { color: #5b6b82; font-size: 12px; }
</style>
