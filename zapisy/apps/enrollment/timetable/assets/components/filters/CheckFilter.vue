<script lang="ts">
import Vue, { PropType } from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class BooleanFilter implements Filter {
  constructor(public on: boolean, public predicate: (c: any) => boolean) {}

  visible(c: any): boolean {
    if (!this.on) {
      return true;
    }
    return this.predicate(c);
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  props: {
    filterKey: String, //unique label
    label: String, //display label
    predicate: Function as PropType<(c: any) => boolean>, //boolean funct on an object - if true, element will be shown.
    onByDefault: { type: Boolean, default: false },
  },
  data: () => {
    return {
      on: false,
    };
  },
  created: function () {
    const searchParams = new URL(window.location.href).searchParams;

    if (searchParams.has(this.filterKey)) {
      if (searchParams.get(this.filterKey) === "true") {
        this.on = true;
      }
    }

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/clearFilters":
          this.on = false;
          break;
      }
    });
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    on: function (newOn: boolean) {
      const url = new URL(window.location.href);
      if (newOn) {
        url.searchParams.set(this.filterKey, newOn.toString());
      } else {
        url.searchParams.delete(this.filterKey);
      }
      window.history.replaceState(null, "", url.toString());

      this.registerFilter({
        k: this.filterKey,
        f: new BooleanFilter(newOn, this.predicate),
      });
    },
  },
});
</script>

<template>
  <div class="input-group">
    <div class="custom-control custom-checkbox">
      <input
        type="checkbox"
        class="custom-control-input"
        :id="filterKey"
        v-model="on"
      />
      <label class="custom-control-label" :for="filterKey">{{ label }}</label>
    </div>
  </div>
</template>
