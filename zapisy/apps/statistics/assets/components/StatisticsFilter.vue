<script lang="ts">
import Vue from "vue";

import TextFilter from "../../../theses/assets/components/filters/TextFilter.vue";
import CheckFilterElastic from "./filters/CheckFilterElastic.vue";
import { mapMutations } from "vuex";


export default Vue.extend({
  components: {
    TextFilter,
    CheckFilterElastic,
  },
  data: function () {
    return {
      sortingModes: [
        ["course_name_asc", "wg nazwy przedmiotu, rosnąco"],
        ["course_name_desc", "wg nazwy przedmiotu, malejąco"],
        ["waiting_students_asc", "wg liczby oczekujących, rosnąco"],
        ["waiting_students_desc", "wg liczby oczekujących, malejąco"],
      ],
      selected: "course_name_asc",
    };
  },
  watch: {
    selected: function (newSelected: string) {
      this.sort(newSelected);
    },
  },
  methods: {
    ...mapMutations("sorting", ["changeSorting"]),
    sort: function (newSelected: string) {
      if (newSelected === "waiting_students_desc") {
        this.changeSorting({
          k: "max_of_waiting_students",
          f: false,
        });
      } else if (newSelected === "waiting_students_asc") {
        this.changeSorting({
          k: "max_of_waiting_students",
          f: true,
        });
      } else if (newSelected === "course_name_asc") {
        this.changeSorting({
          k: "course_name",
          f: true,
        });
      } else if (newSelected === "course_name_desc") {
        this.changeSorting({
          k: "course_name",
          f: false,
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
        <div class="col-lg-5">
          <TextFilter
            filterKey="title-filter"
            :properties="['course_name']"
            placeholder="Nazwa przedmiotu"
          />
        </div>
        <div class="col-lg-4">
          <div class="input-group mb-2">
            <select class="form-select" v-model="selected">
              <option v-for="[k, o] of sortingModes" :value="k">
                {{ o }}
              </option>
            </select>
          </div>
        </div>
      </div>
      <div class="row">
          <CheckFilterElastic
            filterKey="filter-has-waiting-students"
            label="Pokaż jedynie przedmioty z oczekującymi studentami"
            :predicate="c => c.max_of_waiting_students > 0"
          />
          <CheckFilterElastic
            filterKey="filter-no-math-subjects"
            label="Ukryj przedmioty matematyczne"
            :predicate="c => !c.course_name.includes('[IM]')"
          />
          <CheckFilterElastic
            filterKey="filter-has-guaranteed-spots"
            label="Pokaż jedynie przedmioty z miejscami gwarantowanymi"
            :predicate="c => c.groups.some(g => g.guaranteed_spots && g.guaranteed_spots.length > 0)"
          />
          <CheckFilterElastic
            filterKey="filter-has-group-below-ten"
            label="Pokaż jedynie przedmioty z przynajmniej jedną grupą poniżej 10 osób"
            :predicate="c => c.groups.some(g => g.enrolled < 10)"
          />
        </div>
    </div>
  </div>
</template>
