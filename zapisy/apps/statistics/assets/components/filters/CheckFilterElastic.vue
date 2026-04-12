<script lang="ts">
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class ElasticFilter implements Filter {
  constructor(public on: boolean, public predicate: (c: any) => boolean) {}

  visible(c: any): boolean {
    if (!this.on) {
      return true;
    }
    return this.predicate(c);
  }
}

//ElasticFilter applies filtering through a given boolean function
export default Vue.extend({
  props: {
    filterKey: String, //unique label
    label: String, //display label
    predicate: Function, //boolean funct on an object - if true, element will be shown.
  },
  data: () => {
    return {
      on: false,
    };
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
  },
  watch: {
    on: function (newOn: boolean) {
      this.registerFilter({
        k: this.filterKey,
        f: new ElasticFilter(newOn, this.predicate),
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
