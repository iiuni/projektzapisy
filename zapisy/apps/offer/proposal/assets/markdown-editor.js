import Vue from "vue/dist/vue.js";
import MarkdownEditor from "./MarkdownEditor.vue";

import { library } from "@fortawesome/fontawesome-svg-core";
import { faMarkdown } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

library.add(faMarkdown);

Vue.component("font-awesome-icon", FontAwesomeIcon);

new Vue({
    el: "#edit-proposal-form",
    components: {
        "markdown-editor": MarkdownEditor
    }
});
