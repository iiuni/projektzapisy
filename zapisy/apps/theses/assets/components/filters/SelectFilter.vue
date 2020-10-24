<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class ExactFilter implements Filter {
  constructor(
    public option: number | string | undefined,
    public propertyName: string
  ) {}

  visible(c: Object): boolean {
    if (this.option === undefined) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => number;
    let propValue = propGetter(c);
    return propValue == this.option;
  }
}

// TextFilter applies the string filtering on a property of a thesis.
export default Vue.extend({
  props: {
    // Property of a thesis on which we are filtering.
    property: String,
    // Every filter needs a unique identifier.
    filterKey: String,
    default: String as () => number | string | undefined,
    options: Array as () => [number | string, string][],
    placeholder: String,
  },
  data: () => {
    return {
      selected: undefined as number | string | undefined,
    };
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  mounted: function () {
    this.selected = this.default;
  },
  watch: {
    selected: function (newSelected: number | string | undefined) {
      this.registerFilter({
        k: this.filterKey,
        f: new ExactFilter(newSelected, this.property),
      });
    },
  },
});
</script>

<template>
  <div class="input-group mb-2">
    <select class="custom-select" v-model="selected">
      <option selected :value="undefined">-- {{ placeholder }} --</option>
      <option v-for="[k, o] of options" :value="k">{{ o }}</option>
    </select>
  </div>
</template>
