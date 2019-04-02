<template>
  <div class="border rounded-sm row no-gutters">
    <div class="col">
        <textarea class="textarea form-control" 
            rows="10" :value="input" :name="name"
            @input="update" @focusin="active = true" @focusout="active = false"></textarea>
    </div>
    <div class="col-12 col-md-6" :hidden="!active">
      <div class="p-3" v-html="compiledMarkdown"></div>
    </div>
      
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
  background-color: #f6f6f6;
}

</style>
