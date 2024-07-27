import { createApp } from "vue";
import MarkdownEditor from "./MarkdownEditor.vue";

document.addEventListener("DOMContentLoaded", function () {
  // <markdown-editor ...> will be a replaced with a widget.
  const elements = document.querySelectorAll("markdown-editor");

  for (const el of elements) {
    const attrName = el.getAttribute("name") || "";
    const attrValue = el.getAttribute("value") || "";
    const attrPlaceholder = el.getAttribute("placeholder") || "";
    const attrIsInvalid = el.classList.contains("is-invalid");

    const app = createApp(MarkdownEditor, {
      name: attrName,
      value: attrValue,
      placeholder: attrPlaceholder,
      is_invalid: attrIsInvalid,
    });
    app.mount(el);
  }
});
