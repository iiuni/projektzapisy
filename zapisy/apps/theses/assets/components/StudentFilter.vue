<script lang="ts">
import Vue from "vue";

import MultiSelectFilter from "@/enrollment/timetable/assets/components/filters/MultiSelectFilter.vue";
import {
  MultiselectFilterData, MultiselectFilterDataItem,
} from "@/enrollment/timetable/assets/models";

export default Vue.extend({
  components: {
    MultiSelectFilter,
  },
  data: function () {
    return {
      students: [] as MultiselectFilterData<number>,
    };
  },
  // created: function () {
    // const students = [
    //   { value: 1, label: "Jan Kowalski (1234567)" },
    //   { value: 2, label: "Anna Nowak (2345678)" },
    //   { value: 3, label: "Piotr Wiśniewski (3456789)" },
    // ];
    // this.students = cloneDeep(students);
  // },
  mounted: function () {
    const djangoField = document.getElementById("id_students");
    if (djangoField === null) {
      return;
    }

    const options = djangoField.querySelectorAll("option");
    this.students = Array.from(options).map((option) => ({
      value: Number(option.value),
      label: option.text,
    } as MultiselectFilterDataItem<number>));

    const selectedOptions = Array.from(options).filter((option) => option.selected);
    const multiselectOptions = selectedOptions.map((option) => ({
      value: Number(option.value),
      label: option.text,
    }));
    console.log(multiselectOptions);
    multiselectOptions.forEach((option) => this.$refs["student-filter"].addToSelection(option));
    console.log(this.$refs["student-filter"]);
  },
  methods: {
    updateDjangoField: function(selectedIds: number[]) {
      const djangoField = document.getElementById("id_students");
      if (djangoField === null) {
        return;
      }

      console.log(this.$refs["student-filter"]);
      
      const options = djangoField.querySelectorAll("option");
      options.forEach((option) => {
        option.selected = selectedIds.includes(Number(option.value));
      });
    }
  },
});
</script>

<template>
  <div class="bg-light filters-card">
    <MultiSelectFilter
      filterKey="student-filter"
      property="student"
      :options="students"
      title="Przypisani studenci"
      placeholder="Szukaj po imieniu, nazwisku, numerze indeksu..."
      ref="student-filter"
      @select="updateDjangoField"
    />
  </div>
</template>

<style lang="scss" scoped>
.filters-card {
  transform: scale(1);
  z-index: 2;
}
</style>
