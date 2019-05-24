<script lang="ts">
// The CourseList component allows the student to select courses presented on
// prototype.
//
// The selection is not persistent. In order to keep a group on prototype the
// student will need to _pin_ it. The state is not maintained by the component.
// This job is handled by the Vuex store (`../store/courses.ts`).
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";

import { Group } from "../models";
import { CourseShell } from "../store/courses";

export type CourseObject = { id: number; name: string; url: string };

@Component({
  props: {
    courses: Array as () => CourseObject[],
  },
  computed: mapGetters("courses", {
    selectionState: "selection"
  }),
})
export default class CourseList extends Vue {
  // The computed property selectionState comes from store.
  selectionState!: number[];
  get selection(): number[] {
    return this.selectionState;
  }
  set selection(value: number[]) {
    this.$store.dispatch("courses/updateSelection", value);
  }
}
</script>

<template>
  <div class="course-list-wrapper">
    <a @click="selection = []">Odznacz wszystkie</a>
    <div class="course-list-sidebar">
      <ul class="course-list-sidebar-inner">
        <li v-for="c of courses" :key="c.id">
          <input type="checkbox" :id="c.id" :value="c.id" v-model="selection">
          <label :for="c.id">{{ c.name }}</label>
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
}

input[type="checkbox"] {
  float: left;
  margin: 5px;
}

label {
  display: block;
  padding-top: 2px;
  padding-left: 30px;
  text-align: left;
  width: auto;
  float: initial;
}

.course-list-wrapper {
  margin-top: 30px;
}

.course-list-sidebar {
  margin-top: 5px;
  overflow-x: hidden;
  overflow-y: auto;
  z-index: 10;
  max-height: 600px;
  box-shadow: 0 0 1px rgba(0, 0, 0, 0.25);
}

.course-list-sidebar-inner {
  padding: 10px;
}
</style>
