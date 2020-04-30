import Vue from "vue/dist/vue";
import MarkdownEditor from "./MarkdownEditor.vue";

// We import the version of Vue that contains template compiler. It only affects
// very few users, and allows us to write <markdown-editor ...> in the template.
// This suppresses the console log.
Vue.config.productionTip = false;
Vue.config.devtools = false;

// <markdown-editor ...> will be a child of the previous sibling of the script
// element.
const me = document.currentScript;
const el = me.previousElementSibling;

new Vue({ el: el, components: { "markdown-editor": MarkdownEditor } });
