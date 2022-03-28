<script lang="ts">
import Vue from "vue";
import { mapMutations, mapGetters } from "vuex";

// TextFilter applies the string filtering on a property of a thesis.
export default Vue.extend({
  props: {
    // Property of a thesis on which we are filtering.
    property: String,
    label: String,
  },
  data: () => {
    return {
      order: 0,
    };
  },
  mounted: function () {
    this.$store.subscribe((mutation, state) => {
      switch (mutation.type) {
        case "sorting/changeSorting":
          if (this.getSortingProperty != this.property) this.order = 0;
          break;
      }
    });
  },
  computed: {
    ...mapGetters("sorting", {
      getSortingProperty: "getProperty",
    }),
  },
  methods: {
    ...mapMutations("sorting", ["changeSorting"]),
    sort: function () {
      if (this.order == 2) {
        this.changeSorting({
          k: "modified",
          f: false,
        });
        this.order = 0;
      } else {
        this.changeSorting({
          k: this.property,
          f: this.order + 1 == 1,
        });
        this.order += 1;
      }
    },
  },
});
</script>

<template>
  <div style="cursor: pointer" v-on:click="sort()">
    {{ label }}
    <span v-if="order == 1">&darr;</span>
    <span v-if="order == 2">&uarr;</span>
  </div>
</template>
