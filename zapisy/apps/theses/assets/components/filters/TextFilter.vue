<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { ThesisInfo } from "../../store/theses";
import { Filter } from "../../store/filters";

class TextFilter implements Filter {
  propGetters: ((c: ThesisInfo) => string)[];

  constructor(public pattern: string = "", public propertyNames: string[]) {
    this.propGetters = this.propertyNames.map((propName) => property(propName));
  }

  visible(c: ThesisInfo): boolean {
    const patternWords = this.pattern.toLocaleLowerCase().split(" ");
    const propValues = this.propGetters.map((f) => f(c).toLocaleLowerCase());
    const patternWordMatches = patternWords.map((w) =>
      propValues.some((v) => v.includes(w))
    );
    return patternWordMatches.every((b) => b);
  }
}

// TextFilter applies the string filtering on a property of a thesis.
export default Vue.extend({
  props: {
    // Properties of a thesis on which we are filtering.
    properties: Array,
    // Every filter needs a unique identifier.
    filterKey: String,
    placeholder: String,
  },
  data: () => {
    return {
      pattern: "",
    };
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    pattern: function (newPattern: string, _) {
      this.registerFilter({
        k: this.filterKey,
        f: new TextFilter(newPattern, this.properties as string[]),
      });
    },
  },
});
</script>

<template>
  <div class="input-group mb-2">
    <input
      class="form-control"
      type="text"
      v-model="pattern"
      :placeholder="placeholder"
    />
    <button
      class="btn btn-outline-secondary"
      type="button"
      @click="pattern = ''"
    >
      &times;
    </button>
  </div>
</template>
