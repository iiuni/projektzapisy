<script lang="ts">
import Vue from "vue";

import TextFilter from "./filters/TextFilter.vue";
import CheckFilter from "./filters/CheckFilter.vue";
import { mapMutations } from "vuex";

export default Vue.extend({
  components: {
    TextFilter,
    CheckFilter,
  },
  data: function () {
    return {
      sortingModes: [
        ["nzsr", "wg niezapisanych studentów, rosnąco"],
        ["nzsm", "wg niezapisanych studentów, malejąco"],
        ["npr", "wg nazwy przedmiotu, rosnąco"],
        ["npm", "wg nazwy przedmiotu, malejąco"],
      ],
      selected: "npr",
    };
  },
  watch: {
    selected: function (newSelected: string) {
      this.sort(newSelected.toString());
    },
  },
  methods: {
    ...mapMutations("sorting", ["changeSorting"]),
    sort: function (newSelected: string) {
      if (newSelected === "nzsm") {
        this.changeSorting({
          k: "max_of_waiting_students",
          f: false,
        });
      } else if (newSelected === "nzsr") {
        this.changeSorting({
          k: "max_of_waiting_students",
          f: true,
        });
      } else if (newSelected === "npr") {
        this.changeSorting({
          k: "alphabetical_sorting_index",
          f: false,
        });
      } else if (newSelected === "npm") {
        this.changeSorting({
          k: "alphabetical_sorting_index",
          f: true,
        });
      }
    },
  },
});
</script>

<template>
  <div class="card bg-light">
    <div class="card-body">
      <div class="row">
        <div class="col-lg-6">
          <TextFilter
            filterKey="title-filter"
            :properties="['course_name']"
            placeholder="Nazwa przedmiotu"
          />
        </div>
        <div class="col-lg-3">
          <div class="input-group mb-2">
            <select class="custom-select" v-model="selected">
              <option selected :value="undefined">-- Sortuj --</option>
              <option v-for="[k, o] of sortingModes" :value="k">
                {{ o }}
              </option>
            </select>
          </div>
        </div>
        <div class="col-lg-3">
          <CheckFilter
            filterKey="available-filter"
            property="max_of_waiting_students"
            label="Pokaż jedynie przedmioty, gdzie są niezapisani studenci"
          />
        </div>
      </div>
    </div>
  </div>
</template>
