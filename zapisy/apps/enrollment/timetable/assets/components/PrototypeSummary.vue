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

  get totalPoints(): number {
    return state.state.totalPoints;
  }
  get totalCourses(): { [id: number]: Course } {
    return state.state.totalCourses;
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
    <SimpleSummary
      summaryType="(P, Z, K, L)"
      :sumPoints="totalPoints"
      :groups="groups"
      :courses="totalCourses"
    />
    <SimpleSummary
      summaryType="(Z)"
      :sumPoints="enrolledPoints"
      :groups="groups"
      :courses="enrolledCourses"
    />
    <SimpleSummary
      summaryType="(K)"
      :sumPoints="queuedPoints"
      :groups="groups"
      :courses="queuedCourses"
    />
    <SimpleSummary
      summaryType="(P)"
      :sumPoints="pinnedPoints"
      :groups="groups"
      :courses="pinnedCourses"
    />
  </div>
</template>
