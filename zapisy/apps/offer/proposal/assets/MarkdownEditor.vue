<template>
  <div class="form-row no-gutter">
    <textarea class="textarea form-control text-monospace"
        :class="{'is-invalid': is_invalid, 'col-md-6': active}"
        rows="10" :value="input" :name="name"
        @input="update" @focusin="active = true" @focusout="active = false"></textarea>
    <div class="border rounded-lg col-md-6 overflow-hidden" v-if="active">
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
