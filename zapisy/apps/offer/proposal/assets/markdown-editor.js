import Vue from "vue/dist/vue.js";
import MarkdownEditor from "./MarkdownEditor.vue";

new Vue({
    el: "form",
    components: {
        "markdown-editor": MarkdownEditor,
    },
});
