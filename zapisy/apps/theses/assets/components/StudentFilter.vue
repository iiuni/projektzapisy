<script lang="ts">
import Vue from "vue";
import { debounce } from "lodash";

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
  /**
   * Load assigned students, if there are any
   */
  mounted: function () {
    const djangoField = document.getElementById(
      "id_students"
    ) as HTMLSelectElement | null;
    if (djangoField === null) {
      return;
    }

    const options = djangoField.options;
    if (options.length === 0) {
      // No one assigned
      return;
    }
    // Map each student from <select> data to MultiSelectFilter data
    const assigned_students: MultiselectFilterData<number> = Array.from(
      options
    ).map((element) => ({
      value: Number(element.value),
      label: element.text,
    }));

    // Store the assigned students to display them after MultiSelectFilter gains focus
    this.students = assigned_students;

    // Mark the students as selected in MultiSelectFilter
    const filter = this.$refs["student-filter"] as Vue &
      MultiSelectFilterWithSelected;
    if (filter) {
      filter.selected = this.students;
    }
  },
  methods: {
    onSelect: function (selectedIds: number[]) {
      // Update the server <select>
      this.updateDjangoField(selectedIds);
    },
    clearData: function () {
      const filter = this.$refs["student-filter"] as Vue &
        MultiSelectFilterWithSelected;

      if (filter) {
        // Leave only assigned students in the dropdown list
        this.students = Array.from(filter.selected);
      }
    },
    updateDjangoField: function (selectedIds: number[]) {
      const djangoField = document.getElementById(
        "id_students"
      ) as HTMLSelectElement | null;
      if (djangoField === null) {
        return;
      }

      const optionArray = Array.from(djangoField.options);
      // Find the newly-selected item
      const newId = selectedIds.find((id) =>
        optionArray.every((option) => option.value !== String(id))
      );
      // Find the unselected item
      const removedIndex = optionArray.findIndex(
        (option) => !selectedIds.includes(Number(option.value))
      );

      // If a new item was selected, add it to the server <select>
      if (newId !== undefined) {
        const newOption = document.createElement("option");
        newOption.value = newId.toString();
        newOption.text = this.students.find((s) => s.value === newId)!.label;
        newOption.selected = true;
        djangoField.options.add(newOption);
      }

      // If an item was unselected, remove it from the server <select>
      if (removedIndex !== -1) {
        djangoField.options.remove(removedIndex);
      }
    },
    fetchStudents: async function (
      substring: string
    ): Promise<{ students: MultiselectFilterData<number> }> {
      const ajaxUrlInput = document.querySelector(
        "input#ajax-url"
      ) as HTMLInputElement | null;

      if (ajaxUrlInput === null) {
        throw new Error("#ajax-url not found.");
      }

      // Get the endpoint URI
      const ajaxUrl = ajaxUrlInput.value;
      const urlSafeSubstring = encodeURIComponent(substring);
      // Fetch students matching the query
      const response = await fetch(`${ajaxUrl}/${urlSafeSubstring}`);
      return response.json();
    },
    onSearchChange: debounce(function (
      this: { updateStudents: (search: string) => void },
      search: string
    ) {
      // Update the dropdown list after changing the search input
      return this.updateStudents(search);
    },
    300),
    updateStudents: async function (search: string) {
      // Remove unselected students from the dropdown
      this.clearData();

      if (search.length === 0) {
        return;
      }

      // Fetch students matching the query
      const { students: fetchedStudents } = await this.fetchStudents(search);

      // Add only the students which are not selected to avoid duplication
      const notSelectedStudents = fetchedStudents.filter((fetchedStudent) =>
        this.students.every((s) => s.value !== fetchedStudent.value)
      );

      this.students.push(...notSelectedStudents);
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
      @select="onSelect"
      @search-change="onSearchChange"
    />
  </div>
</template>

<style lang="scss" scoped>
.filters-card {
  transform: scale(1);
  z-index: 2;
}
</style>
