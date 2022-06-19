<script lang="ts">
import Vue from "vue";
// import { mapGetters } from "vuex";
import Component from "vue-class-component";
import { values } from "lodash";
// import { getCurrentInstance } from "vue";

// const current = getCurrentInstance();
import state from "../store/groups";
import { DayOfWeek, nameDay, Course, Group } from "../models";
import SimpleSummary from "./SimpleSummary.vue";

// export type CourseObject = { id: number; name: string; url: string };
@Component({
  components: {
    SimpleSummary,
  },
  computed: {
    // ...mapGetters("courses", {
    //   sumPointsState: "sumPoints",
    // }),
    // ...mapGetters("filters", {
    //   tester: "visible",
    // }),
  },
})
export default class PrototypeSummary extends Vue {
  // The computed property selectionState comes from store.
  //   selectionState!: number[];
  //   // The same goes for courses and tester.
  //   courses!: CourseInfo[];
  //   tester!: (_: CourseInfo) => boolean;
  public summary1: Boolean = false;
  public summary2: Boolean = false;
  public summary3: Boolean = false;
  public summary4: Boolean = false;

  public selectedGroups: Function = (group: Group, course: Course) =>
    !group.isEnrolled &&
    !group.isEnqueued &&
    !group.isPinned &&
    group.isSelected &&
    group.course.id == course.id;

  public pinnedGroups: Function = (group: Group, course: Course) =>
    !group.isEnrolled &&
    !group.isEnqueued &&
    group.isPinned &&
    group.course.id == course.id;

  public enqueuedGroups: Function = (group: Group, course: Course) =>
    group.isEnqueued && group.course.id == course.id;

  public enrolledGroups: Function = (group: Group, course: Course) =>
    group.isEnrolled && group.course.id == course.id;

  get selectedPoints(): number {
    return state.state.selectedPoints;
  }
  get selectedCourses(): { [id: number]: Course } {
    return state.state.selectedCourses;
  }
  get enrolledPoints(): number {
    return state.state.enrolledPoints;
  }
  get enrolledCourses(): { [id: number]: Course } {
    return state.state.enrolledCourses;
  }
  get queuedPoints(): number {
    return state.state.queuedPoints;
  }
  get queuedCourses(): { [id: number]: Course } {
    return state.state.queuedCourses;
  }
  get pinnedPoints(): number {
    return state.state.pinnedPoints;
  }
  get pinnedCourses(): { [id: number]: Course } {
    return state.state.pinnedCourses;
  }
  get groups(): { [id: number]: Group } {
    return values(state.state.store).filter(
      (g) => g.isEnrolled || g.isEnqueued || g.isPinned || g.isSelected
    );
  }
  public GetNameDay(day: DayOfWeek) {
    return nameDay(day);
  }
  // set sumPoints(newValue: number): {
  //   state.state.sumPoints = newValue;
  // }

  // The list should be initialised to contain courses filtered with initial filters
  // fetched from the query string and then apply filters whenever they update.
  //   visibleCourses: CourseInfo[] = [];
  //   methods: {
  // this.visibleCourses = this.courses.filter(this.tester);

  // this.$store.subscribe((mutation, state) => {
  //   switch (mutation.type) {
  //     case "filters/registerFilter":
  //       this.visibleCourses = this.courses.filter(this.tester);
  //       break;
  //   }
  // });
  //   }
}
</script>

<template>
  <div class="table-responsiveVUE">
    <button type="button" class="summary" @click="summary1 = !summary1">
      (L)
    </button>
    <button type="button" class="summary" @click="summary2 = !summary2">
      (Z)
    </button>
    <button type="button" class="summary" @click="summary3 = !summary3">
      (K)
    </button>
    <button type="button" class="summary" @click="summary4 = !summary4">
      (P)
    </button>
    <div v-if="summary1">
      <SimpleSummary
        summaryType="(L)"
        :sumPoints="selectedPoints"
        :groups="groups"
        :courses="selectedCourses"
        :groupsCondition="selectedGroups"
        :key="JSON.stringify(selectedCourses)"
      />
    </div>
    <div v-if="summary2">
      <SimpleSummary
        summaryType="(Z)"
        :sumPoints="enrolledPoints"
        :groups="groups"
        :courses="enrolledCourses"
        :groupsCondition="enrolledGroups"
        :key="JSON.stringify(enrolledCourses)"
      />
    </div>
    <div v-if="summary3">
      <SimpleSummary
        summaryType="(K)"
        :sumPoints="queuedPoints"
        :groups="groups"
        :courses="queuedCourses"
        :groupsCondition="enqueuedGroups"
        :key="JSON.stringify(queuedCourses)"
      />
    </div>
    <div v-if="summary4">
      <SimpleSummary
        v-if="summary4"
        summaryType="(P)"
        :sumPoints="pinnedPoints"
        :groups="groups"
        :courses="pinnedCourses"
        :groupsCondition="pinnedGroups"
        :key="JSON.stringify(pinnedCourses)"
      />
    </div>
  </div>
</template>

<style>
.summary {
  display: inline-block;
}
</style>
