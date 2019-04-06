<template>
  <div class="">
    <textarea class="textarea form-control text-monospace"
        :class="{'is-invalid': is_invalid}"
        rows="10" :value="input" :name="name" :placeholder="placeholder"
        @input="update" @focusin="active = true" @focusout="active = false"></textarea>
    <div class="border rounded-lg" :hidden="!active">
      <small class="text-muted m-2">Podgląd:</small>
      <div class="preview p-3" v-html="compiledMarkdown"></div>
    </div>
      
    <slot></slot>
  </div>
</template>

<script>
import marked from "marked";
import { debounce } from "lodash";

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
    }
  },
  data: function() {
    return {
      input: this.value ? this.value : "",
      active: false,
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

textarea {
  height: 100%;
}

.preview {
  overflow: hidden;
}

</style>
