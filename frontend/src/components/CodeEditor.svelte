<script>
  import { onMount, onDestroy } from "svelte";
  import { EditorView, basicSetup } from "codemirror";
  import { EditorState } from "@codemirror/state";
  import { python } from "@codemirror/lang-python";
  import { sql } from "@codemirror/lang-sql";
  import { oneDark } from "@codemirror/theme-one-dark";

  let { code = "", language = "python", onChange } = $props();

  let host;
  let editor;

  onMount(() => {
    const langExt = language === "sql" ? sql() : python();
    editor = new EditorView({
      parent: host,
      state: EditorState.create({
        doc: code,
        extensions: [
          basicSetup,
          langExt,
          oneDark,
          EditorView.updateListener.of((v) => {
            if (v.docChanged && onChange) onChange(editor.state.doc.toString());
          }),
          EditorView.theme({ "&": { fontSize: "13.5px" }, ".cm-content": { fontFamily: "ui-monospace, SFMono-Regular, Menlo, monospace" } }),
        ],
      }),
    });
  });

  onDestroy(() => editor && editor.destroy());
</script>

<div class="editor" bind:this={host}></div>

<style>
  .editor :global(.cm-editor) {
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid #2a3344;
    max-height: 420px;
  }
  .editor :global(.cm-scroller) { overflow: auto; }
</style>
