<script lang="ts">
import { isEmpty, property } from "lodash";
import Vue from "vue";
import Multiselect from 'vue-multiselect'
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class ExactMultiFilter implements Filter {
  constructor(public ids: number[], public propertyName: string) {}

  visible(c: Object): boolean {
    if (isEmpty(this.ids)) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => number;
    let propValue = propGetter(c);
    return this.ids.includes(propValue);
  }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
  components: {
    Multiselect
  },
  props: {
    property: String,
    filterKey: String,
    options: Array as () => [number, string][],
    placeholder: String,
  },
  data: () => {
    return {
      selected: [],
      optionsObjs: []
    };
  },
  created: function () {
    this.optionsObjs = this.options.map(([a, b]) => {return {id: Number(a), name: b}});
    this.placeholderDecorated = '-- ' + this.placeholder + ' --';

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
  },
  watch: {
    selected: function (newSelected: string | undefined) {
      const selectedIds = this.selected.map((el) => {return el.id});

      this.registerFilter({
        k: this.filterKey,
        f: new ExactMultiFilter(selectedIds, this.property),
      });
    },
  },
});
</script>

<style src="vue-multiselect/dist/vue-multiselect.min.css"></style>

<template>
  <div class="input-group mb-2">
    <multiselect v-model="selected" :options="optionsObjs" :multiple="true" :close-on-select="true" :clear-on-select="true"
        :searchable="false" :allow-empty="true" :placeholder="placeholderDecorated" track-by="id" label="name"
        selectLabel="" selectedLabel="" deselectLabel="">
    </multiselect>
  </div>
</template>