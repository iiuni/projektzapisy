<script lang="ts">
import Vue from "vue";

import TextFilter from "../../../theses/assets/components/filters/TextFilter.vue";
import CheckFilter from "../../../theses/assets/components/filters/CheckFilter.vue";
import { mapMutations } from "vuex";
import { CourseInfo } from "../store/courses";

export default Vue.extend({
  components: {
    TextFilter,
    CheckFilter,
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
    ...mapMutations("filters", ["clearFilters"]),
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
    guaranteedGTZ: function (course: CourseInfo) {
      return course.total_guaranteed > 0;
    },
    waitingGTZ: function (course: CourseInfo) {
      return course.total_waiting > 0;
    },
    hasGroupBelowTen: function (course: CourseInfo) {
      return course.smallest_group < 10;
    },
    isNotMat: function (course: CourseInfo) {
      return course.is_math == false;
    },
    hasTypeWithDeficit: function (course: CourseInfo) {
      return course.has_deficit;
    },
  },
});
</script>

<template>
  <div class="card bg-light">
    <div class="card-body">
      <div class="row">
        <div class="col-lg-6">
          <div class="row">
            <div class="col-12">
              <TextFilter
                filterKey="title-filter"
                :properties="['course_name']"
                placeholder="Nazwa przedmiotu"
              />
            </div>
            <div class="col-12">
              <div class="input-group mb-2">
                <select class="form-select" v-model="selected">
                  <option v-for="[k, o] of sortingModes" :value="k">
                    {{ o }}
                  </option>
                </select>
              </div>
            </div>
            <div class="col-12">
              <button
                class="btn btn-outline-secondary"
                type="button"
                @click="clearFilters()"
              >
                Wyczyść filtry
              </button>
            </div>
          </div>
        </div>
        <div class="col-lg-6">
          <CheckFilter
            filterKey="filter-has-waiting-students"
            label="Pokaż jedynie przedmioty z oczekującymi studentami"
            :predicate="waitingGTZ"
          />
          <CheckFilter
            filterKey="filter-no-math-subjects"
            label="Ukryj przedmioty matematyczne"
            :predicate="isNotMat"
            :onByDefault="true"
          />
          <CheckFilter
            filterKey="filter-has-guaranteed-spots"
            label="Pokaż jedynie przedmioty z miejscami gwarantowanymi"
            :predicate="guaranteedGTZ"
          />
          <CheckFilter
            filterKey="filter-has-more-waiting-than-free"
            label="Ukryj przedmioty z większą liczbą wolnych miejsc niż liczbą oczekujących"
            :predicate="hasTypeWithDeficit"
          />
          <CheckFilter
            filterKey="filter-has-group-below-ten"
            label="Pokaż jedynie przedmioty z przynajmniej jedną grupą poniżej 10 osób"
            :predicate="hasGroupBelowTen"
          />
        </div>
      </div>
    </div>
  </div>
</template>
