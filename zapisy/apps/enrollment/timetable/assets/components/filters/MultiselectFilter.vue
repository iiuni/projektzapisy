<script lang="ts">
import { isEmpty, property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class ExactFilter implements Filter {
  constructor(public ids: string[], public propertyName: string) {}

  visible(c: Object): boolean {
    if (isEmpty(this.ids)) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => string;
    let propValue = propGetter(c);
    return this.ids.includes(propValue);
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  props: {
    // Property of a course on which we are filtering.
    property: String,
    // Every filter needs a unique identifier.
    filterKey: String,
    options: Array as () => [string, string][],
    title: String,
    placeholder: String,
  },
  data: () => {
    return {
      selected: [] as string[],
    };
  },
  created: function () {
    const searchParams = new URL(window.location.href).searchParams;
    if (searchParams.has(this.property)) {
      this.selected = searchParams.get(this.property)!.split(",");
    }

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/clearFilters":
          this.selected = [];
          break;
      }
    });
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
    clearFilter() {
      this.selected = [];
    },
  },
  watch: {
    selected: function () {
      const selectedIds = this.selected;

      const url = new URL(window.location.href);
      if (isEmpty(selectedIds)) {
        url.searchParams.delete(this.property);
      } else {
        url.searchParams.set(this.property, selectedIds.join(","));
      }
      window.history.replaceState(null, "", url.toString());

      this.registerFilter({
        k: this.filterKey,
        f: new ExactFilter(selectedIds, this.property),
      });
    },
  },
});
</script>

<template>
  <div class="mb-2">
    <h4>{{ title }}</h4>
    <select
      multiple
      v-model="selected"
      :size="Math.min(options.length, 5)"
      class="custom-select"
    >
      <option
        v-if="placeholder"
        :value="undefined"
        @click.prevent="clearFilter()"
        class="font-italic text-secondary"
      >
        {{ placeholder }}
      </option>
      <option v-for="[k, o] of options" :value="k">
        {{ o }}
      </option>
    </select>
  </div>
</template>
