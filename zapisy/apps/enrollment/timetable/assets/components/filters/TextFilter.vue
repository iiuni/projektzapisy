<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { CourseInfo } from "../../store/courses";
import { Filter, getSearchParams, LAST_FILTER_KEY } from "../../store/filters";

class TextFilter implements Filter {
  constructor(
    public pattern: string = "",
    public propertyName: string
  ) {}

  visible(c: CourseInfo): boolean {
    let propGetter = property(this.propertyName) as (c: CourseInfo) => string;
    let propValue = propGetter(c);
    return propValue
      .toLocaleLowerCase()
      .includes(this.pattern.toLocaleLowerCase());
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  props: {
    // Property of a course on which we are filtering.
    property: String,
    // Every filter needs a unique identifier.
    filterKey: String,
    placeholder: String,
    // Which CourseFilter component is it used on
    appID: String,
  },
  data: () => {
    return {
      pattern: "",
    };
  },
  created: function () {
    const searchParams = getSearchParams();

    if (searchParams.has(this.appID + "_" + this.property)) {
      // TypeScript doesn't infer that property is present, manual cast required.
      this.pattern = searchParams.get(
        this.appID + "_" + this.property
      ) as string;
    }

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/clearFilters":
          this.pattern = "";
          break;
      }
    });
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    pattern: function (newPattern: string, _) {
      const searchParams = getSearchParams();
      if (newPattern.length == 0) {
        searchParams.delete(this.appID + "_" + this.property);
        sessionStorage.removeItem(LAST_FILTER_KEY);
        if (searchParams.toString().length != 0) {
          sessionStorage.setItem(LAST_FILTER_KEY, searchParams.toString());
        }
      } else {
        searchParams.set(this.appID + "_" + this.property, newPattern);
        sessionStorage.setItem(LAST_FILTER_KEY, searchParams.toString());
      }

      this.registerFilter({
        k: this.filterKey,
        f: new TextFilter(newPattern, this.property),
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
