<template>
  <div
    class="md-editor-wrapper form-control"
    :class="{ 'is-invalid': is_invalid }"
  >
    <textarea
      class="form-control text-monospace bg-light"
      rows="10"
      :value="input"
      :name="name"
      :placeholder="placeholder"
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
    <slot></slot>
  </div>
</template>

<script>
import { faMarkdown } from "@fortawesome/free-brands-svg-icons/faMarkdown";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { debounce, uniqueId } from "lodash";
import MarkdownIt from "markdown-it";

const md = MarkdownIt({
  linkify: true,
  typographer: true,
  quotes: "„”«»",
});

export default {
  props: {
    name: String,
    value: {
      type: String,
      required: false,
    },
    placeholder: String,
    is_invalid: {
      type: Boolean,
      default: false,
      required: false,
    },
  },
  data: function () {
    return {
      input: this.value ? this.value : "",
      faMarkdown: faMarkdown,
    };
  },
  computed: {
    compiledMarkdown: function () {
      return md.render(this.input);
    },
  },
  methods: {
    update: debounce(function (e) {
      this.input = e.target.value;
    }, 300),
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
  padding: 0;
  height: auto;

  @media (max-width: 767px) {
    flex-direction: column;
  }
  textarea {
    @media (min-width: 768px) {
      width: calc(50% - 0.25em);
      border-top-right-radius: 0;
      border-bottom-right-radius: 0;
    }
    padding: 1em;
    border: none;
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
