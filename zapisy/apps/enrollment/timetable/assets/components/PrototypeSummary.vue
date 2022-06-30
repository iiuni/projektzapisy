<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { values, cloneDeep } from "lodash";

import state from "../store/groups";
import { Course, Group } from "../models";
import SimpleSummary from "./SimpleSummary.vue";

@Component({
  components: {
    SimpleSummary,
  },
})
export default class PrototypeSummary extends Vue {
  public points: number = 0;

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
    let enrolledCourses: { [id: number]: Course } = {};
    let enrolledPoints: number = 0;
    Object.entries(groups).forEach((g) => {
      if (g[1].isEnrolled && enrolledCourses[g[1].course.id] === undefined) {
        enrolledCourses[g[1].course.id] = cloneDeep(g[1].course);
        enrolledCourses[g[1].course.id].summaryPoints =
          enrolledCourses[g[1].course.id].points;
        enrolledPoints += enrolledCourses[g[1].course.id].summaryPoints;
      }
    });
    let enqueuedCourses: { [id: number]: Course } = {};
    let enqueuedPoints: number = 0;
    Object.entries(groups).forEach((g) => {
      if (g[1].isEnqueued && enqueuedCourses[g[1].course.id] === undefined) {
        enqueuedCourses[g[1].course.id] = cloneDeep(g[1].course);
        if (enrolledCourses[g[1].course.id] === undefined) {
          enqueuedCourses[g[1].course.id].summaryPoints =
            enqueuedCourses[g[1].course.id].points;
        } else {
          enqueuedCourses[g[1].course.id].summaryPoints = 0;
        }
        enrolledPoints += enqueuedCourses[g[1].course.id].summaryPoints;
      }
    });
    let pinnedCourses: { [id: number]: Course } = {};
    let pinnedPoints: number = 0;
    Object.entries(groups).forEach((g) => {
      if (
        g[1].isPinned &&
        !g[1].isEnrolled &&
        !g[1].isEnqueued &&
        pinnedCourses[g[1].course.id] === undefined
      ) {
        pinnedCourses[g[1].course.id] = cloneDeep(g[1].course);
        if (
          enrolledCourses[g[1].course.id] === undefined &&
          enqueuedCourses[g[1].course.id] === undefined
        ) {
          pinnedCourses[g[1].course.id].summaryPoints =
            pinnedCourses[g[1].course.id].points;
        } else {
          pinnedCourses[g[1].course.id].summaryPoints = 0;
        }
        pinnedPoints += pinnedCourses[g[1].course.id].summaryPoints;
      }
    });
    let selectedCourses: { [id: number]: Course } = {};
    let selectedPoints: number = 0;
    Object.entries(groups).forEach((g) => {
      if (
        g[1].isSelected &&
        !g[1].isPinned &&
        !g[1].isEnrolled &&
        !g[1].isEnqueued &&
        selectedCourses[g[1].course.id] === undefined
      ) {
        selectedCourses[g[1].course.id] = cloneDeep(g[1].course);
        if (
          enrolledCourses[g[1].course.id] === undefined &&
          enqueuedCourses[g[1].course.id] === undefined &&
          pinnedCourses[g[1].course.id] === undefined
        ) {
          selectedCourses[g[1].course.id].summaryPoints =
            selectedCourses[g[1].course.id].points;
        } else {
          selectedCourses[g[1].course.id].summaryPoints = 0;
        }
        selectedPoints += selectedCourses[g[1].course.id].summaryPoints;
      }
    });
    this.points =
      selectedPoints + pinnedPoints + enqueuedPoints + enrolledPoints;
    return {
      enrolledCourses: enrolledCourses,
      enqueuedCourses: enqueuedCourses,
      pinnedCourses: pinnedCourses,
      selectedCourses: selectedCourses,
      enrolledPoints: enrolledPoints,
      enqueuedPoints: enqueuedPoints,
      pinnedPoints: pinnedPoints,
      selectedPoints: selectedPoints,
    };
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
}
</script>

<template>
  <div class="table-responsiveVUE">
    <table id="enr-schedule-listByCourseVUE" class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Przedmiot</th>
          <th class="ects" scope="col">ECTS</th>
        </tr>
      </thead>
      <SimpleSummary
        summaryType="(Z)"
        :groups="groups"
        :groupsCondition="enrolledGroups"
        :courses="enrolledSummary[0]"
        :points="enrolledSummary[1]"
      />
      <SimpleSummary
        summaryType="(K)"
        :groups="groups"
        :groupsCondition="enqueuedGroups"
        :courses="enqueuedSummary[0]"
        :points="enqueuedSummary[1]"
      />
      <SimpleSummary
        summaryType="(P)"
        :groups="groups"
        :groupsCondition="pinnedGroups"
        :courses="pinnedSummary[0]"
        :points="pinnedSummary[1]"
      />
      <SimpleSummary
        summaryType="(L)"
        :groups="groups"
        :groupsCondition="selectedGroups"
        :courses="selectedSummary[0]"
        :points="selectedSummary[1]"
      />
      <tfoot>
        <tr>
          <td>
            <strong>Suma punktów ECTS łącznie:</strong>
          </td>
          <td class="ects">{{ points }}</td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<style>
thead {
  width: 100%;
}
th.ects {
  text-align: right;
}
</style>
