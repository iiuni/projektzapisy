<script setup lang="ts">
import { ref, watch } from "vue";
import TextFilter from "../../../theses/assets/components/filters/TextFilter.vue";
import CheckFilter from "../../../theses/assets/components/filters/CheckFilter.vue";
import { useStore } from "vuex";
const store = useStore();

const sortingModes = [
  ["course_name_asc", "wg nazwy przedmiotu, rosnąco"],
  ["course_name_desc", "wg nazwy przedmiotu, malejąco"],
  ["waiting_students_asc", "wg liczby oczekujących, rosnąco"],
  ["waiting_students_desc", "wg liczby oczekujących, malejąco"],
];
const selected = ref("course_name_asc");
const changeSorting = (newSelected: string) => {
  if (newSelected === "waiting_students_desc") {
    store.commit("sorting/changeSorting", {
      k: "max_of_waiting_students",
      f: false,
    });
  } else if (newSelected === "waiting_students_asc") {
    store.commit("sorting/changeSorting", {
      k: "max_of_waiting_students",
      f: true,
    });
  } else if (newSelected === "course_name_asc") {
    store.commit("sorting/changeSorting", { k: "course_name", f: true });
  } else if (newSelected === "course_name_desc") {
    store.commit("sorting/changeSorting", { k: "course_name", f: false });
  }
};

watch(selected, changeSorting);
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
        <div class="col-lg-3">
          <CheckFilter
            filterKey="available-filter"
            property="max_of_waiting_students"
            label="Pokaż jedynie przedmioty z oczekującymi studentami"
          />
        </div>
      </div>
    </div>
  </div>
</template>
