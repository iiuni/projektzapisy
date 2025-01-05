<script lang="ts">
// This particular CourseList component extends the functionality of other
// CourseList components by allowing the student to select courses
// presented on the prototype timetable.
//
// The selection is not persistent. In order to keep a group on prototype the
// student will need to _pin_ it. The state is not maintained by the component.
// This job is handled by the Vuex store (`../store/courses.ts`).
import Vue from "vue";
import { mapGetters } from "vuex";
import { CourseInfo } from "../store/courses";

// This component is used in the timetable-prototype-component webpack
export default Vue.extend({
  data() {
    return {
      visibleCourses: [] as CourseInfo[],
    };
  },
  computed: {
    // The selection state and courses list are provided by their
    // respective getters in the Vuex store.
    ...mapGetters("courses", {
      selectionState: "selection",
      courses: "courses",
    }),
    ...mapGetters("filters", {
      tester: "visible",
    }),
    // selection is a local property that binds the selection values from input
    // and calls update in the Vuex store.
    selection: {
      get(): number[] {
        return this.selectionState;
      },
      set(value: number[]) {
        this.$store.dispatch("courses/updateSelection", value);
      },
    },
  },
  mounted() {
    // When mounted, apply initial filters fetched from the query string
    // on the loaded list of courses.
    this.visibleCourses = this.courses.filter(this.tester);

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.filter(this.tester);
          break;
      }
    });
  },
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
