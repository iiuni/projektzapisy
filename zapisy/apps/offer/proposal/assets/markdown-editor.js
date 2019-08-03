import Vue from "vue/dist/vue.js";
import MarkdownEditor from "./MarkdownEditor.vue";

new Vue({
    el: "#edit-proposal-form",
    components: {
        "markdown-editor": MarkdownEditor,
    },
});
