<script lang="ts">
import Vue from "vue";
// import { mapGetters } from "vuex";
import Component from "vue-class-component";
import { values, cloneDeep } from "lodash";
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

  public selectedCourses: { [id: number]: Course } = {};
  public selectedPoints: number = 0;

  public pinnedCourses: { [id: number]: Course } = {};
  public pinnedPoints: number = 0;

  public enqueuedCourses: { [id: number]: Course } = {};
  public enqueuedPoints: number = 0;

  public enrolledCourses: { [id: number]: Course } = {};
  public enrolledPoints: number = 0;

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
  
  public initializeCourses() {
    let groups: { [id: number]: Group } = values(state.state.store).filter(
      (g) => g.isEnrolled || g.isEnqueued || g.isPinned || g.isSelected
    );
    let enrolledCourses = {};
    let enrolledPoints = 0;
    Object.entries(groups).forEach((g) => {
          if (g[1].isEnrolled && enrolledCourses[g[1].course.id] === undefined) {
            enrolledCourses[g[1].course.id] = cloneDeep(g[1].course);
            enrolledCourses[g[1].course.id].summaryPoints = enrolledCourses[g[1].course.id].points;
            enrolledPoints += enrolledCourses[g[1].course.id].summaryPoints;
          }
        });
    let enqueuedCourses = {};
    let enqueuedPoints = 0;
    Object.entries(groups).forEach((g) => {
      if (g[1].isEnqueued && enqueuedCourses[g[1].course.id] === undefined) {
        enqueuedCourses[g[1].course.id] = cloneDeep(g[1].course);
        if (enrolledCourses[g[1].course.id] === undefined) {
              enqueuedCourses[g[1].course.id].summaryPoints = enqueuedCourses[g[1].course.id].points;
            } else {
              enqueuedCourses[g[1].course.id].summaryPoints = 0;
            }
        enrolledPoints += enqueuedCourses[g[1].course.id].summaryPoints;
      }
    });
    let pinnedCourses = {};
    let pinnedPoints = 0;
    Object.entries(groups).forEach((g) => {
      if (g[1].isPinned && !g[1].isEnrolled && !g[1].isEnqueued && pinnedCourses[g[1].course.id] === undefined) {
        pinnedCourses[g[1].course.id] = cloneDeep(g[1].course);
        if (enrolledCourses[g[1].course.id] === undefined && 
            enqueuedCourses[g[1].course.id] === undefined) {              
              pinnedCourses[g[1].course.id].summaryPoints = pinnedCourses[g[1].course.id].points;
            } else {
              pinnedCourses[g[1].course.id].summaryPoints = 0;
            }
        pinnedPoints += pinnedCourses[g[1].course.id].summaryPoints;
      }
    });
    let selectedCourses = {};
    let selectedPoints = 0;
    Object.entries(groups).forEach((g) => {
      if (g[1].isSelected && !g[1].isPinned && !g[1].isEnrolled && !g[1].isEnqueued && selectedCourses[g[1].course.id] === undefined) {
        selectedCourses[g[1].course.id] = cloneDeep(g[1].course);
        if (enrolledCourses[g[1].course.id] === undefined && 
            enqueuedCourses[g[1].course.id] === undefined && 
            pinnedCourses[g[1].course.id] === undefined) {              
              selectedCourses[g[1].course.id].summaryPoints = selectedCourses[g[1].course.id].points;
            } else {
              selectedCourses[g[1].course.id].summaryPoints = 0;
            }
        selectedPoints += selectedCourses[g[1].course.id].summaryPoints;
      }
    });
    return {enrolledCourses: enrolledCourses, enqueuedCourses: enqueuedCourses, 
            pinnedCourses: pinnedCourses, selectedCourses: selectedCourses, 
            enrolledPoints: enrolledPoints, enqueuedPoints: enqueuedPoints,
            pinnedPoints: pinnedPoints, selectedPoints: selectedPoints};
  }

  get pinnedSummary(): [{ [id: number]: Course }, number] {
    let courses = this.initializeCourses();
    return [courses.pinnedCourses, courses.pinnedPoints];
  }

  get enrolledSummary(): [{ [id: number]: Course }, number] {
    let courses = this.initializeCourses();
    return [courses.enrolledCourses, courses.enrolledPoints];
  }

  get enqueuedSummary(): [{ [id: number]: Course }, number] {
    let courses = this.initializeCourses();
    return [courses.enqueuedCourses, courses.enqueuedPoints];
  }

  get selectedSummary(): [{ [id: number]: Course }, number] {
    let courses = this.initializeCourses();
    return [courses.selectedCourses, courses.selectedPoints];
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
        :groups="groups"
        :groupsCondition="selectedGroups"
        :courses="selectedSummary[0]"
        :points="selectedSummary[1]"
      />
    </div>
    <div v-if="summary2">
      <SimpleSummary
        summaryType="(Z)"
        :groups="groups"
        :groupsCondition="enrolledGroups"
        :courses="enrolledSummary[0]"
        :points="enrolledSummary[1]"
      />
    </div>
    <div v-if="summary3">
      <SimpleSummary
        summaryType="(K)"
        :groups="groups"
        :groupsCondition="enqueuedGroups"
        :courses="enqueuedSummary[0]"
        :points="enqueuedSummary[1]"
      />
    </div>
    <div v-if="summary4">
      <SimpleSummary
        v-if="summary4"
        :groups="groups"
        :groupsCondition="pinnedGroups"
        :courses="pinnedSummary[0]"
        :points="pinnedSummary[1]"
      />
    </div>    
  </div>
</template>

<style>
.summary {
  display: inline-block;
}
</style>
