<script>
  import { tick } from "svelte";
  import { marked } from "marked";
  import { api } from "../lib/api.js";
  import { view } from "../lib/stores.js";

  const THREADS_KEY = "dojo-chat-threads-v1";
  const SIZE_KEY = "dojo-chat-size-v1";
  const GENERAL = "__general__";

  function loadThreads() {
    try { return JSON.parse(localStorage.getItem(THREADS_KEY)) || {}; }
    catch { return {}; }
  }
  function loadSize() {
    try {
      const s = JSON.parse(localStorage.getItem(SIZE_KEY));
      if (s && s.w && s.h) return s;
    } catch {}
    return { w: 390, h: 520 };
  }

  let open = $state(false);
  let mode = $state("tutor");
  let input = $state("");
  let busy = $state(false);
  let threads = $state(loadThreads()); // { threadId: [{role,text}] }
  let size = $state(loadSize());
  let msgsEl;

  // Which thread are we in? An exercise's id, or the shared general thread.
  let threadId = $derived($view.name === "exercise" ? $view.exerciseId : GENERAL);
  let currentExerciseId = $derived($view.name === "exercise" ? $view.exerciseId : null);
  let messages = $derived(threads[threadId] || []);

  function persist() {
    try { localStorage.setItem(THREADS_KEY, JSON.stringify(threads)); } catch {}
  }

  function pushMessage(id, msg) {
    threads = { ...threads, [id]: [...(threads[id] || []), msg] };
    persist();
  }

  // Replace the text of the most recent tutor message (the streaming placeholder).
  function updateLastTutor(id, text) {
    const arr = [...(threads[id] || [])];
    for (let i = arr.length - 1; i >= 0; i--) {
      if (arr[i].role === "tutor") { arr[i] = { ...arr[i], text }; break; }
    }
    threads = { ...threads, [id]: arr };
    persist();
    scrollToBottom();
  }

  async function scrollToBottom() {
    await tick();
    if (msgsEl) msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  // auto-scroll when the visible thread changes or grows
  $effect(() => { messages.length; threadId; open; scrollToBottom(); });

  async function send() {
    const q = input.trim();
    if (!q || busy) return;
    const id = threadId;
    pushMessage(id, { role: "you", text: q });
    pushMessage(id, { role: "tutor", text: "" }); // streaming placeholder
    input = ""; busy = true;
    try {
      await api.chatStream(q, mode, currentExerciseId, null, (full) => {
        updateLastTutor(id, full);
      });
    } catch (e) {
      updateLastTutor(id, "(error: " + e.message + ")");
    } finally { busy = false; }
  }

  function onKey(e) {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  }

  function clearThread() {
    threads = { ...threads, [threadId]: [] };
    persist();
  }

  // ---- resize (drag the top-left grip) ----
  function startResize(e) {
    e.preventDefault();
    const startX = e.clientX, startY = e.clientY;
    const startW = size.w, startH = size.h;
    const move = (ev) => {
      const w = Math.min(900, Math.max(330, startW + (startX - ev.clientX)));
      const h = Math.min(window.innerHeight * 0.9, Math.max(320, startH + (startY - ev.clientY)));
      size = { w, h };
    };
    const up = () => {
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
      try { localStorage.setItem(SIZE_KEY, JSON.stringify(size)); } catch {}
    };
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  }

  const render = (t) => marked.parse(t || "");
  let threadLabel = $derived(threadId === GENERAL ? "General" : "This exercise");
</script>

<button class="fab" onclick={() => (open = !open)}>{open ? "✕ Close" : "💬 Ask"}</button>

{#if open}
  <div class="chat" style="width:{size.w}px; height:{size.h}px">
    <div class="grip" onpointerdown={startResize} title="Drag to resize">
      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M13 1 L1 13 M13 6 L6 13 M13 11 L11 13" stroke="#6b7d96" stroke-width="1.4" stroke-linecap="round"/>
      </svg>
    </div>

    <div class="chead">
      <span class="ttl">🧑‍🏫 Dojo Tutor <span class="scope">· {threadLabel}</span></span>
      <div class="right">
        <div class="toggle">
          <button class:active={mode === "tutor"} onclick={() => (mode = "tutor")}>Tutor</button>
          <button class:active={mode === "explain"} onclick={() => (mode = "explain")}>Explain</button>
        </div>
        {#if messages.length}
          <button class="clear" title="Clear this thread" onclick={clearThread}>🗑</button>
        {/if}
      </div>
    </div>

    <div class="msgs" bind:this={msgsEl}>
      {#if messages.length === 0}
        <p class="empty">
          {#if threadId === GENERAL}
            Ask anything about backend or this app. Open an exercise to get help tied to it.
          {:else}
            Questions here are about <b>this exercise</b> and remember your past mistakes.
          {/if}
          <br /><b>Tutor</b> nudges with hints; <b>Explain</b> answers directly.
        </p>
      {/if}
      {#each messages as m}
        <div class="msg {m.role}">
          {#if m.role === "tutor"}
            {#if m.text}
              <div class="bubble md">{@html render(m.text)}</div>
            {:else}
              <div class="bubble thinking"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>
            {/if}
          {:else}
            <div class="bubble">{m.text}</div>
          {/if}
        </div>
      {/each}
    </div>

    <div class="composer">
      <textarea bind:value={input} onkeydown={onKey} rows="2"
                placeholder={currentExerciseId ? "Ask about this exercise…" : "Ask a question…"}></textarea>
      <button onclick={send} disabled={busy}>Send</button>
    </div>
  </div>
{/if}

<style>
  .fab {
    position: fixed; bottom: 22px; right: 22px; z-index: 40;
    background: linear-gradient(135deg, #2f6df6, #7a3af0); color: #fff; border: none;
    padding: 12px 18px; border-radius: 30px; font-weight: 700; cursor: pointer;
    box-shadow: 0 6px 24px rgba(47,109,246,0.4); font-size: 14px;
  }
  .chat {
    position: fixed; bottom: 78px; right: 22px; z-index: 40;
    display: flex; flex-direction: column;
    background: #11161f; border: 1px solid #2a3344; border-radius: 16px; overflow: hidden;
    box-shadow: 0 12px 48px rgba(0,0,0,0.5);
  }
  .grip {
    position: absolute; top: 0; left: 0; width: 22px; height: 22px;
    display: grid; place-items: center; cursor: nwse-resize; z-index: 2;
    border-bottom-right-radius: 8px; background: #161d29aa;
  }
  .chead { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px 12px 26px; border-bottom: 1px solid #1f2735; color: #e8eef6; font-weight: 700; font-size: 14px; }
  .ttl .scope { color: #6b7d96; font-weight: 500; font-size: 12px; }
  .right { display: flex; align-items: center; gap: 8px; }
  .toggle { display: flex; background: #0f141d; border-radius: 8px; padding: 2px; }
  .toggle button { background: none; border: none; color: #8aa0bd; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; }
  .toggle button.active { background: #2f6df6; color: #fff; }
  .clear { background: none; border: none; cursor: pointer; font-size: 13px; opacity: 0.7; }
  .clear:hover { opacity: 1; }
  .msgs { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
  .empty { color: #6b7d96; font-size: 13px; line-height: 1.6; }
  .msg { display: flex; }
  .msg.you { justify-content: flex-end; }
  .bubble { max-width: 88%; padding: 9px 12px; border-radius: 12px; font-size: 13.5px; line-height: 1.5; }
  .msg.you .bubble { background: #2f6df6; color: #fff; border-bottom-right-radius: 3px; white-space: pre-wrap; }
  .msg.tutor .bubble { background: #161d29; color: #d6e2f2; border: 1px solid #232d3e; border-bottom-left-radius: 3px; }
  .thinking { display: flex; gap: 4px; align-items: center; }
  .dot { width: 6px; height: 6px; border-radius: 50%; background: #6b7d96; animation: blink 1.3s infinite both; }
  .dot:nth-child(2) { animation-delay: 0.18s; }
  .dot:nth-child(3) { animation-delay: 0.36s; }
  @keyframes blink { 0%, 80%, 100% { opacity: 0.25; } 40% { opacity: 1; } }
  .composer { display: flex; gap: 8px; padding: 10px; border-top: 1px solid #1f2735; }
  .composer textarea { flex: 1; resize: none; background: #0f141d; border: 1px solid #232d3e; border-radius: 9px; color: #e8eef6; padding: 8px; font-size: 13px; font-family: inherit; }
  .composer button { background: #2f6df6; color: #fff; border: none; border-radius: 9px; padding: 0 16px; font-weight: 700; cursor: pointer; }
  .composer button:disabled { opacity: 0.5; }

  /* markdown rendering inside tutor bubbles */
  .md :global(h1), .md :global(h2), .md :global(h3), .md :global(h4) { color: #eef4fb; margin: 10px 0 5px; font-size: 14px; line-height: 1.3; }
  .md :global(h1) { font-size: 16px; }
  .md :global(p) { margin: 6px 0; }
  .md :global(ul), .md :global(ol) { margin: 6px 0; padding-left: 20px; }
  .md :global(li) { margin: 3px 0; }
  .md :global(code) { background: #0e131c; padding: 1px 5px; border-radius: 4px; font-size: 12px; color: #8fd0ff; font-family: ui-monospace, Menlo, monospace; }
  .md :global(pre) { background: #0e131c; border: 1px solid #232d3e; padding: 10px; border-radius: 8px; overflow-x: auto; margin: 8px 0; }
  .md :global(pre code) { background: none; padding: 0; color: #d6e2f2; }
  .md :global(strong) { color: #eef4fb; }
  .md :global(a) { color: #6ea8ff; }
  .md :global(blockquote) { border-left: 3px solid #2f6df6; margin: 8px 0; padding: 2px 12px; color: #aebfd6; }
  .md :global(:first-child) { margin-top: 0; }
  .md :global(:last-child) { margin-bottom: 0; }
</style>
