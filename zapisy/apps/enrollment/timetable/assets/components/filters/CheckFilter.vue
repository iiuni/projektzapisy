<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter, LAST_FILTER_KEY, getSearchParams } from "../../store/filters";

class BooleanFilter implements Filter {
  constructor(
    public on: boolean,
    public propertyName: string,
  ) {}

  visible(c: Object): boolean {
    if (!this.on) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => boolean;
    let propValue = propGetter(c);
    return propValue;
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  props: {
    // Property of a course on which we are filtering.
    property: String,
    // Every filter needs a unique identifier.
    filterKey: String,
    label: String,
    // Which CourseFilter component is it used on.
    appID: String,
  },
  data: () => {
    return {
      on: false,
    };
  },
  created: function () {
    const searchParams = getSearchParams();

    if (searchParams.has(this.appID + "_" + this.property)) {
      if (searchParams.get(this.appID + "_" + this.property) === "true") {
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
      const searchParams = getSearchParams();
      if (!newOn) {
        searchParams.delete(this.appID + "_" + this.property);
        sessionStorage.removeItem(LAST_FILTER_KEY);
        if (searchParams.toString().length != 0) {
          sessionStorage.setItem(LAST_FILTER_KEY, searchParams.toString());
        }
      } else {
        searchParams.set(this.appID + "_" + this.property, newOn.toString());
        sessionStorage.setItem(LAST_FILTER_KEY, searchParams.toString());
      }

      this.registerFilter({
        k: this.filterKey,
        f: new BooleanFilter(newOn, this.property),
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
