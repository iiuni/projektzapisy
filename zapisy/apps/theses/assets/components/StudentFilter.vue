<script lang="ts">
import Vue from "vue";

import MultiSelectFilter from "@/enrollment/timetable/assets/components/filters/MultiSelectFilter.vue";
import {
  MultiselectFilterData,
  MultiselectFilterDataItem,
} from "@/enrollment/timetable/assets/models";

type MultiSelectFilterWithSelected = {
  selected: MultiselectFilterDataItem<number>[];
};

export default Vue.extend({
  components: {
    MultiSelectFilter,
  },
  data: function () {
    return {
      students: [] as MultiselectFilterData<number>,
    };
  },
  mounted: function () {
    const djangoField = document.getElementById("id_students");
    if (djangoField === null) {
      return;
    }

    const djangoOptions = djangoField.querySelectorAll("option");
    this.students = Array.from(djangoOptions).map(
      (option) =>
        ({
          value: Number(option.value),
          label: option.text,
        } as MultiselectFilterDataItem<number>)
    );

    const selectedOptions = Array.from(djangoOptions).filter(
      (option) => option.selected
    );
    const multiselectOptions = this.students.filter((dataItem) =>
      selectedOptions.some(
        (selectedOption) => Number(selectedOption.value) === dataItem.value
      )
    );

    const filter = this.$refs["student-filter"] as Vue &
      MultiSelectFilterWithSelected;
    if (filter) {
      filter.selected = multiselectOptions;
    }
  },
  methods: {
    updateDjangoField: function (selectedIds: number[]) {
      const djangoField = document.getElementById("id_students");
      if (djangoField === null) {
        return;
      }

      const options = djangoField.querySelectorAll("option");
      options.forEach((option) => {
        option.selected = selectedIds.includes(Number(option.value));
      });
    },
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
