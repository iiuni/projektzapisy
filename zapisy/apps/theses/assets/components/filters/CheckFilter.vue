<script lang="ts">
import Vue from "vue";
import { mapMutations } from "vuex";
import { PropType } from "vue";

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

//BooleanFilter applies filtering through a given boolean predicate
export default Vue.extend({
  props: {
    filterKey: String, //unique label
    label: String, //display label
    predicate: Function as PropType<(c: any) => boolean>, //boolean funct on an object - if true, element will be shown.
    onByDefault: { type: Boolean, default: false },
  },
  data() {
    return {
      on: this.onByDefault,
    };
  },
  created() {
    this.$store.subscribe((mutation) => {
      if (mutation.type === "filters/clearFilters") {
        this.on = false;
      }
    });
  },
  mounted() {
    this.registerFilter({
      k: this.filterKey,
      f: new BooleanFilter(this.on, this.predicate),
    });
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    on: function (newOn: boolean) {
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
