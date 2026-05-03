<script lang="ts">
import Vue from "vue";

import TextFilter from "../../../theses/assets/components/filters/TextFilter.vue";
import CheckFilter from "../../../theses/assets/components/filters/CheckFilter.vue";
import { mapMutations } from "vuex";


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
    totalGuaranteed: function(course){
    return (course.groups || []).reduce((total, g) => {
      return total + (g.guaranteed_spots || []).reduce((sum, s) => sum + (s.limit || 0), 0);
    }, 0);
    },
    totalEnrolled: function(course){
      return (course.groups || []).reduce((sum, group) => sum + (group.enrolled || 0), 0);
    },
    totalLimit: function(course){
      return (course.groups || []).reduce((sum, group) => sum + (group.limit || 0), 0);
    },
    totalAvailable: function(course)
    {
      return this.totalLimit(course) - this.totalEnrolled(course);
    },
    totalWaiting: function(course){
      return (course.groups || []).reduce((sum, group) => sum + (group.queued || 0), 0);
    },
    hasGroupBelowTen: function(course){
      return course.groups.some(g => g.enrolled < 10);
    },
    mathTest: function(course){
      return course.course_type != "Matematyczny"
    },
    hasTypeWithDeficit: function (course){
      const groups = course.groups || [];

      const grouped = groups.reduce((acc, g) => {
        if (!acc[g.type_name]) {
          acc[g.type_name] = [];
        }
        acc[g.type_name].push(g);
        return acc;
      }, {} as Record<string, any[]>);//any can be replaced with GroupInfo if imported

      return Object.values(grouped).some(groupList=> {
        const totalLimit = groupList.reduce((sum, g) => sum + (g.limit || 0), 0);
        const totalEnrolled = groupList.reduce((sum, g) => sum + (g.enrolled || 0), 0);
        const totalWaiting = groupList.reduce((sum, g) => sum + (g.queued || 0), 0);

        const totalAvailable = totalLimit - totalEnrolled;

        return totalWaiting > totalAvailable;
      });
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
          </div>
        </div>
        <div class="col-lg-6">
          <CheckFilter
            filterKey="filter-has-waiting-students"
            label="Pokaż jedynie przedmioty z oczekującymi studentami"
            :predicate="c => totalWaiting(c) > 0"
          />
          <CheckFilter
            filterKey="filter-no-math-subjects"
            label="Ukryj przedmioty matematyczne" 
            :predicate="c => !c.course_name.includes('[IM]')"
            :defaultOn="true"
          />
          <CheckFilter
            filterKey="filter-has-guaranteed-spots"
            label="Pokaż jedynie przedmioty z miejscami gwarantowanymi"
            :predicate="c => totalGuaranteed(c) > 0"
          />
          <CheckFilter
            filterKey="filter-has-more-waiting-than-free"
            label="Ukryj przedmioty z większą liczbą wolnych miejsc niż liczbą oczekujących"
            :predicate="c => totalAvailable(c) < totalWaiting(c)"
          />
          <CheckFilter
            filterKey="filter-has-group-below-ten"
            label="Pokaż jedynie przedmioty z przynajmniej jedną grupą poniżej 10 osób"
            :predicate="hasGroupBelowTen"
          />
          <CheckFilter
            filterKey="test-filter"
            label="Filtr Testowy (Free > Waiting)" 
            :predicate="hasTypeWithDeficit"
            :defaultOn="true"
          />
        </div>
      </div>
    </div>
  </div>
</template>
