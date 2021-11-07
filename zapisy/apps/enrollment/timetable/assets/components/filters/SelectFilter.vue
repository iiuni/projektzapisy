<script lang="ts">
import { isUndefined, property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class ExactFilter implements Filter {
  constructor(public option: string | undefined, public propertyName: string) {}

  visible(c: Object): boolean {
    if (this.option === undefined) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => string;
    let propValue = propGetter(c);
    return propValue == this.option;
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  props: {
    // Property of a course on which we are filtering.
    property: String,
    // Every filter needs a unique identifier.
    filterKey: String,
    options: Array as () => [number, string][],
    placeholder: String,
  },
  data: () => {
    return {
      selected: undefined,
    };
  },
  created: function() {
    const searchParams = new URL(window.location.href).searchParams;
    const isChosenKey = ([key, _]) => searchParams.get(this.filterKey) == key;

    if(searchParams.has(this.filterKey) && this.options.some(isChosenKey)) {
      // Set selection from URL only if respective key is in search params
      // and its value is a valid option.
      this.$data.selected = searchParams.get(this.filterKey);
    }
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    selected: function (newSelected: string | undefined) {
      const url = new URL(window.location.href);
      if (isUndefined(newSelected)) {
        url.searchParams.delete(this.filterKey);
      } else {
        url.searchParams.set(this.filterKey, newSelected.toString());
      }
      window.history.replaceState(null, null, url);

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
      <option v-for="[k, o] of options" :value="k">
        {{ o }}
      </option>
    </select>
  </div>
</template>
