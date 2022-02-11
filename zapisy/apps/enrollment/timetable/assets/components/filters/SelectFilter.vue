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
      selected: undefined as string | undefined,
    };
  },
  created: function () {
    const searchParams = new URL(window.location.href).searchParams;
    const isChosenKey = ([key, _]: [number, string]) =>
      searchParams.get(this.property) == key.toString();

    if (searchParams.has(this.property) && this.options.some(isChosenKey)) {
      // TypeScript doesn't infer that property is present, manual cast required.
      this.selected = searchParams.get(this.property) as string;
    }

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/clearFilters":
          this.selected = undefined;
          break;
      }
    });
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    selected: function (newSelected: string | undefined) {
      const url = new URL(window.location.href);
      if (isUndefined(newSelected)) {
        url.searchParams.delete(this.property);
      } else {
        url.searchParams.set(this.property, newSelected.toString());
      }
      window.history.replaceState(null, "", url.toString());

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
