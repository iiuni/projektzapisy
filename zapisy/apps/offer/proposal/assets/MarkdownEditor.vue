<template>
  <div>
    <div class="md-editor-wrapper">
      <textarea
          :class="{'is-invalid': is_invalid}"
          rows="10" :value="input" :name="name"
          @input="update"></textarea>
      <div class="preview">
        <span v-html="compiledMarkdown"></span>
        <a
         class="doc-link"
         href="https://guides.github.com/features/mastering-markdown/#examples"
         target="_blank">
          <font-awesome-icon :icon="['fab', 'markdown']" />
        </a>
      </div>
    </div>
    <slot></slot>
  </div>
</template>

<script>
import marked from "marked";
import { debounce, uniqueId } from "lodash";

export default {
  props: {
    name: String,
    value: {
      type: String,
      required: false,
    },
    is_invalid: {
      type: Boolean,
      default: false,
      required: false,
    }
  },
  data: function() {
    return {
      input: this.value ? this.value : "",
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
  }
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
    border: none;
    background: #f8f9fa;
    font-family: SFMono-Regular,Menlo,Monaco,Consolas,Liberation Mono,Courier New,monospace;

    @media (min-width: 768px) {
      width: calc(50% - .25em);
    }
    padding: 1em;
  }

  .preview {
    @media (min-width: 768px) {
      width: calc(50% - .25em);
    }
    position: relative;
    padding: 1em;

    .doc-link {
      color: black;
      position: absolute;
      bottom: .25em;
      right: .5em;
    }
  }
}
</style>