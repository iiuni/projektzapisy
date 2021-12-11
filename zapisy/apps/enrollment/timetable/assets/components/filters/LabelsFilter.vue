<script lang="ts">
import { property, intersection, isEmpty, keys, fromPairs } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";
import { KVDict } from "../../models";

class IntersectionFilter implements Filter {
  constructor(public ids: number[] = [], public propertyName: string) {}

  visible(c: Object): boolean {
    if (isEmpty(this.ids)) {
      return true;
    }
    const propGetter = property(this.propertyName) as (c: Object) => number[];
    const propValue = propGetter(c);
    const common = intersection(this.ids, propValue);
    return !isEmpty(common);
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  props: {
    // Property of a course on which we are filtering.
    property: String,
    // Every filter needs a unique identifier.
    filterKey: String,
    allLabels: Object as () => KVDict,
    title: String,
    // CSS class to apply to the badge when it's on.
    onClass: String,
  },
  computed: {
    allLabelIds: function () {
      return keys(this.allLabels).map((id) => parseInt(id, 10));
    },
  },
  data: () => {
    return {
      selected: {} as { [k: number]: boolean },
    };
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
    toggle(id: number) {
      this.selected[id] = !this.selected[id];
      this._afterSelectionChanged();
    },
    _afterSelectionChanged() {
      const selectedIds = this.allLabelIds.filter((id) => this.selected[id]);

      const url = new URL(window.location.href);
      if (selectedIds.length > 0) {
        url.searchParams.set(this.property, selectedIds.join(","));
      } else {
        url.searchParams.delete(this.property);
      }
      window.history.replaceState(null, "", url.toString());

      this.registerFilter({
        k: this.filterKey,
        f: new IntersectionFilter(selectedIds, this.property),
      });
    },
  },
  // When the component is created we set all the labels as unselected
  // and then set those specified in the query string as selected.
  created: function () {
    this.selected = fromPairs(this.allLabelIds.map((k) => [k, false]));

    const searchParams = new URL(window.location.href).searchParams;
    if (searchParams.has(this.property)) {
      const selectedIds = searchParams
        .get(this.property)!
        .split(",")
        .map((id) => parseInt(id, 10))
        .filter((id) => !isNaN(id));

      selectedIds.forEach((id) => (this.selected[id] = true));

      this.registerFilter({
        k: this.filterKey,
        f: new IntersectionFilter(selectedIds, this.property),
      });
    }

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/clearFilters":
          this.allLabelIds.forEach((id) => {
            this.selected[id] = false;
          });
          this._afterSelectionChanged();
          break;
      }
    });
  },
});
</script>

<template>
  <div class="mb-3 overflow-hidden">
    <h4>{{ title }}</h4>
    <a
      href="#"
      v-for="l in allLabelIds"
      class="badge"
      v-bind:class="[selected[l] ? onClass : 'badge-secondary']"
      @click.prevent="toggle(l)"
    >
      {{ allLabels[l] }}
    </a>
  </div>
</template>
