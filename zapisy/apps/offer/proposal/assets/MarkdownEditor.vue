<template>
    <div>
        <div class="md-editor-wrapper">
            <textarea
                class="text-monospace form-control bg-light"
                :class="{ 'is-invalid': is_invalid }"
                rows="10"
                :value="input"
                :name="name"
                @input="update"
            ></textarea>
            <div class="preview">
                <span v-html="compiledMarkdown"></span>
                <a
                    class="doc-link"
                    href="https://guides.github.com/features/mastering-markdown/#examples"
                    target="_blank"
                >
                    <font-awesome-icon :icon="faMarkdown" />
                </a>
            </div>
        </div>
        <slot></slot>
    </div>
</template>

<script>
import { faMarkdown } from "@fortawesome/free-brands-svg-icons";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import marked from "marked";
import { debounce, uniqueId } from "lodash";

export default {
    props: {
        name: String,
        value: {
            type: String,
            required: false
        },
        is_invalid: {
            type: Boolean,
            default: false,
            required: false
        }
    },
    data: function() {
        return {
            input: this.value ? this.value : "",
            faMarkdown: faMarkdown,
        };
    },
    computed: {
        compiledMarkdown: function() {
            return marked(this.input, { sanitize: true });
        }
    },
    methods: {
        update: debounce(function(e) {
            this.input = e.target.value;
        }, 300)
    },

    components: {
      FontAwesomeIcon,
    },
};
</script>

<style lang="scss" scoped>
.md-editor-wrapper {
    display: flex;
    align-items: stretch;
    justify-content: space-between;

    @media (max-width: 767px) {
        flex-direction: column;
    }

    border: 1px solid #ced4da;
    border-radius: 0.25rem;

    textarea {
        @media (min-width: 768px) {
            width: calc(50% - 0.25em);
            border-top-right-radius: 0;
            border-bottom-right-radius: 0;
        }
        padding: 1em;
    }

    .preview {
        @media (min-width: 768px) {
            width: calc(50% - 0.25em);
        }
        position: relative;
        padding: 1em;

        .doc-link {
            color: black;
            position: absolute;
            bottom: 0.25em;
            right: 0.5em;
        }
    }
}
</style>
