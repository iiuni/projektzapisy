<template>
  <div>
    <nav>
      <div class="nav nav-tabs" role="tablist">
        <a class="nav-item nav-link active" data-toggle="tab" role="tab" :href="`#editor-${id}`">Edytor</a>
        <a class="nav-item nav-link" data-toggle="tab" role="tab" :href="`#preview-${id}`">Podgląd</a>
      </div>
    </nav>
    <div class="tab-content">
      <div class="tab-pane fade show active py-2" role="tabpanel" :id="`editor-${id}`">
        <textarea class="textarea form-control text-monospace bg-light"
        :class="{'is-invalid': is_invalid}"
        rows="10" :value="input" :name="name"
        @input="update"></textarea>
      </div>
      <div class="tab-pane fade" role="tabpanel" :id="`preview-${id}`">
        <div class="preview p-3 border border-top-0 rounded-bottom" v-html="compiledMarkdown"></div>
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
      id: uniqueId('mde-'),
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
.nav-link {
  font-size: smaller;
  padding: .25em .5em;
}
</style>