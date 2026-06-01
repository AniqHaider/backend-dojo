<script>
  import { api } from "../lib/api.js";
  import { view } from "../lib/stores.js";

  let open = $state(false);
  let mode = $state("tutor");
  let input = $state("");
  let busy = $state(false);
  let messages = $state([]); // {role: 'you'|'tutor', text}

  let currentExerciseId = $derived($view.name === "exercise" ? $view.exerciseId : null);

  async function send() {
    const q = input.trim();
    if (!q || busy) return;
    messages = [...messages, { role: "you", text: q }];
    input = ""; busy = true;
    try {
      const { answer } = await api.chat(q, mode, currentExerciseId);
      messages = [...messages, { role: "tutor", text: answer }];
    } catch (e) {
      messages = [...messages, { role: "tutor", text: "(error: " + e.message + ")" }];
    } finally { busy = false; }
  }

  function onKey(e) { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } }
</script>

<button class="fab" onclick={() => (open = !open)}>{open ? "✕" : "💬 Ask"}</button>

{#if open}
  <div class="chat">
    <div class="chead">
      <span>🧑‍🏫 Dojo Tutor</span>
      <div class="toggle">
        <button class:active={mode === "tutor"} onclick={() => (mode = "tutor")}>Tutor</button>
        <button class:active={mode === "explain"} onclick={() => (mode = "explain")}>Explain</button>
      </div>
    </div>

    <div class="msgs">
      {#if messages.length === 0}
        <p class="empty">
          Ask anything. <b>Tutor</b> mode nudges you with hints and remembers your mistakes;
          <b>Explain</b> mode answers directly.
        </p>
      {/if}
      {#each messages as m}
        <div class="msg {m.role}"><div class="bubble">{m.text}</div></div>
      {/each}
      {#if busy}<div class="msg tutor"><div class="bubble thinking">thinking…</div></div>{/if}
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
    width: 380px; max-height: 70vh; display: flex; flex-direction: column;
    background: #11161f; border: 1px solid #2a3344; border-radius: 16px; overflow: hidden;
    box-shadow: 0 12px 48px rgba(0,0,0,0.5);
  }
  .chead { display: flex; align-items: center; justify-content: space-between; padding: 12px 14px; border-bottom: 1px solid #1f2735; color: #e8eef6; font-weight: 700; font-size: 14px; }
  .toggle { display: flex; background: #0f141d; border-radius: 8px; padding: 2px; }
  .toggle button { background: none; border: none; color: #8aa0bd; padding: 4px 10px; border-radius: 6px; cursor: pointer; font-size: 12px; }
  .toggle button.active { background: #2f6df6; color: #fff; }
  .msgs { flex: 1; overflow-y: auto; padding: 14px; display: flex; flex-direction: column; gap: 10px; }
  .empty { color: #6b7d96; font-size: 13px; line-height: 1.5; }
  .msg { display: flex; }
  .msg.you { justify-content: flex-end; }
  .bubble { max-width: 85%; padding: 9px 12px; border-radius: 12px; font-size: 13.5px; line-height: 1.5; white-space: pre-wrap; }
  .msg.you .bubble { background: #2f6df6; color: #fff; border-bottom-right-radius: 3px; }
  .msg.tutor .bubble { background: #161d29; color: #d6e2f2; border: 1px solid #232d3e; border-bottom-left-radius: 3px; }
  .thinking { color: #8aa0bd; font-style: italic; }
  .composer { display: flex; gap: 8px; padding: 10px; border-top: 1px solid #1f2735; }
  .composer textarea { flex: 1; resize: none; background: #0f141d; border: 1px solid #232d3e; border-radius: 9px; color: #e8eef6; padding: 8px; font-size: 13px; font-family: inherit; }
  .composer button { background: #2f6df6; color: #fff; border: none; border-radius: 9px; padding: 0 16px; font-weight: 700; cursor: pointer; }
  .composer button:disabled { opacity: 0.5; }
</style>
