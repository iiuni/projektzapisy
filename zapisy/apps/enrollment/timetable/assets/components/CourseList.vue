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

import { CourseInfo } from "../store/courses";

export type CourseObject = { id: number; name: string; url: string };

@Component({
  computed: {
    ...mapGetters("courses", {
      selectionState: "selection",
      courses: "courses",
    }),
    ...mapGetters("filters", {
      tester: "visible",
    }),
  },
})
export default class CourseList extends Vue {
  // The computed property selectionState comes from store.
  selectionState!: number[];
  // The same goes for courses and tester.
  courses!: CourseInfo[];
  tester!: (_: CourseInfo) => boolean;

  get selection(): number[] {
    return this.selectionState;
  }
  set selection(value: number[]) {
    this.$store.dispatch("courses/updateSelection", value);
  }

  // The list should be initialised to contain courses filtered with initial filters
  // fetched from the query string and then apply filters whenever they update.
  visibleCourses: CourseInfo[] = [];
  mounted() {
    this.visibleCourses = this.courses.filter(this.tester);

    this.$store.subscribe((mutation, state) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.filter(this.tester);
          break;
      }
    });
  }
}
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
            :id="c.id"
            :value="c.id"
            v-model="selection"
            class="custom-control-input"
          />
          <label :for="c.id" class="custom-control-label">{{ c.name }}</label>
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
