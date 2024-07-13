<script setup lang="ts">
// The CourseList component allows the student to select courses presented on
// prototype.
//
// The selection is not persistent. In order to keep a group on prototype the
// student will need to _pin_ it. The state is not maintained by the component.
// This job is handled by the Vuex store (`../store/courses.ts`).
import { ComputedRef } from "vue";
import { onMounted, ref } from "vue";
import { CourseInfo } from "../store/courses";
export type CourseObject = { id: number; name: string; url: string };

import { computed, getCurrentInstance } from "vue";
// TODO: use store from vuex4
const useStore = () => {
  const vm = getCurrentInstance();
  if (!vm) throw new Error("must be called in setup");
  return vm.proxy!.$store;
};
const store = useStore();

const courses: ComputedRef<CourseInfo[]> = computed(
  () => store.getters["courses/courses"]
);
const tester = computed(() => store.getters["filters/visible"]);
const selection = computed({
  get: () => store.state.courses.selection,
  set: (value: number[]) => store.dispatch("courses/updateSelection", value),
});

const visibleCourses = ref<CourseInfo[]>([]);

onMounted(() => {
  visibleCourses.value = courses.value.filter(tester.value);
  // TODO do we subscribe in onMounted or setup?
  store.subscribe((mutation, state) => {
    switch (mutation.type) {
      case "filters/registerFilter":
        visibleCourses.value = courses.value.filter(tester.value);
        break;
    }
  });
});
</script>

<template>
  <div class="course-list-wrapper">
    <a class="btn btn-small btn-light" @click="selection = []"
      >Odznacz wszystkie</a
    >
    <div class="course-list-sidebar">
      <ul class="course-list-sidebar-inner">
        <li
          v-for="c of visibleCourses"
          :key="c.id"
          class="custom-control custom-checkbox"
        >
          <input
            type="checkbox"
            :id="'' + c.id"
            :value="c.id"
            v-model="selection"
            class="custom-control-input"
          />
          <label :for="'' + c.id" class="custom-control-label">{{
            c.name
          }}</label>
        </li>
      </ul>
    </div>
  </div>
</template>

<style lang="scss" scoped>
li {
  clear: left;
  padding-bottom: 8px;
}

ul {
  list-style: none;
  margin: 0;
  padding-left: 0;
}

input[type="checkbox"] {
  float: left;
  margin: 5px;
}

label {
  display: block;
  text-align: left;
  width: auto;
  float: initial;
}

.course-list-sidebar-inner {
  padding-top: 1rem;
}
</style>
