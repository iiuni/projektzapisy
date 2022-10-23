<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import { Group } from "../models";
import SimpleSummary from "./SimpleSummary.vue";
import { CourseWithGroups } from "./SimpleSummary.vue";

const SimpleSummaryProps = Vue.extend({
  props: {
    groups: {
      type: Array as () => Array<Group>,
      default() {
        return [];
      },
    },
  },
});

@Component({
  components: {
    SimpleSummary,
  },
})
export default class PrototypeSummary extends SimpleSummaryProps {
  enrolledSummaryActive: Boolean = false;
  enqueuedSummaryActive: Boolean = false;
  pinnedSummaryActive: Boolean = false;
  selectedSummaryActive: Boolean = false;

  get enrolledSummary(): CourseWithGroups[] {
    let enrolledCourses = new Set(
      this.groups.filter((g) => g.isEnrolled).map((g) => g.course.id)
    );

    if (enrolledCourses.size == 0) {
      this.enrolledSummaryActive = false;
      return [];
    }

    let summaryData: Array<CourseWithGroups> = [];
    for (let course of enrolledCourses) {
      let groups = this.groups.filter(
        (g) => g.isEnrolled && g.course.id == course
      );

      if (groups.length == 0) {
        continue;
      }

      this.enrolledSummaryActive = true;

      summaryData.push(new CourseWithGroups(groups[0].course, groups, false));
    }
    return summaryData;
  }

  get enqueuedSummary(): CourseWithGroups[] {
    let enqueuedCourses = new Set(
      this.groups.filter((g) => g.isEnqueued).map((g) => g.course.id)
    );
    if (enqueuedCourses.size == 0) {
      this.enqueuedSummaryActive = false;
      return [];
    }

    let enrolledCourses = new Set(
      this.groups.filter((g) => g.isEnrolled).map((g) => g.course.id)
    );

    let summaryData: Array<CourseWithGroups> = [];
    for (let course of enqueuedCourses) {
      let groups = this.groups.filter(
        (g) => !g.isEnrolled && g.isEnqueued && g.course.id == course
      );

      if (groups.length == 0) {
        continue;
      }

      let courseIsOverlapping = enrolledCourses.has(course);
      this.enqueuedSummaryActive = true;

      summaryData.push(
        new CourseWithGroups(groups[0].course, groups, courseIsOverlapping)
      );
    }
    return summaryData;
  }

  get pinnedSummary(): CourseWithGroups[] {
    let pinnedCourses = new Set(
      this.groups.filter((g) => g.isPinned).map((g) => g.course.id)
    );
    if (pinnedCourses.size == 0) {
      this.pinnedSummaryActive = false;
      return [];
    }

    let enrolledCourses = new Set(
      this.groups.filter((g) => g.isEnrolled).map((g) => g.course.id)
    );
    let enqueuedCourses = new Set(
      this.groups.filter((g) => g.isEnqueued).map((g) => g.course.id)
    );

    let summaryData: Array<CourseWithGroups> = [];
    for (let course of pinnedCourses) {
      let groups = this.groups.filter(
        (g) =>
          !g.isEnrolled && !g.isEnqueued && g.isPinned && g.course.id == course
      );

      if (groups.length == 0) {
        continue;
      }

      let courseIsOverlapping =
        enrolledCourses.has(course) || enqueuedCourses.has(course);
      this.pinnedSummaryActive = true;

      summaryData.push(
        new CourseWithGroups(groups[0].course, groups, courseIsOverlapping)
      );
    }
    return summaryData;
  }

  get selectedSummary(): CourseWithGroups[] {
    let selectedCourses = new Set(
      this.groups.filter((g) => g.isSelected).map((g) => g.course.id)
    );
    if (selectedCourses.size == 0) {
      this.selectedSummaryActive = false;
      return [];
    }

    let enrolledCourses = new Set(
      this.groups.filter((g) => g.isEnrolled).map((g) => g.course.id)
    );
    let enqueuedCourses = new Set(
      this.groups.filter((g) => g.isEnqueued).map((g) => g.course.id)
    );
    let pinnedCourses = new Set(
      this.groups.filter((g) => g.isPinned).map((g) => g.course.id)
    );

    let summaryData: Array<CourseWithGroups> = [];
    for (let course of selectedCourses) {
      let groups = this.groups.filter(
        (g) =>
          !g.isEnrolled &&
          !g.isEnqueued &&
          !g.isPinned &&
          g.isSelected &&
          g.course.id == course
      );

      if (groups.length == 0) {
        continue;
      }

      let courseIsOverlapping =
        enrolledCourses.has(course) ||
        enqueuedCourses.has(course) ||
        pinnedCourses.has(course);
      this.selectedSummaryActive = true;

      summaryData.push(
        new CourseWithGroups(groups[0].course, groups, courseIsOverlapping)
      );
    }
    return summaryData;
  }

  public countActiveCategories() {
    return (
      Number(this.enrolledSummaryActive) +
      Number(this.enqueuedSummaryActive) +
      Number(this.pinnedSummaryActive) +
      Number(this.selectedSummaryActive)
    );
  }

  public getTotalPointsFromAllCategories() {
    let enrolledCourses = new Set(
      this.groups.filter((g) => g.isEnrolled).map((g) => g.course.id)
    );
    let enqueuedCourses = new Set(
      this.groups.filter((g) => g.isEnqueued).map((g) => g.course.id)
    );
    let pinnedCourses = new Set(
      this.groups.filter((g) => g.isPinned).map((g) => g.course.id)
    );
    let selectedCourses = new Set(
      this.groups.filter((g) => g.isSelected).map((g) => g.course.id)
    );

    let courses = this.union(enrolledCourses, enqueuedCourses);
    courses = this.union(courses, pinnedCourses);
    courses = this.union(courses, selectedCourses);

    let sum = 0;
    this.groups.forEach((g) => {
      if (courses.has(g.course.id)) {
        sum += g.course.points;
        courses.delete(g.course.id);
      }
    });

    return sum;
  }

  private union(setA: Set<Number>, setB: Set<Number>) {
    const _union = new Set(setA);
    for (const elem of setB) {
      _union.add(elem);
    }
    return _union;
  }
}
</script>

<template>
  <div class="table-responsive">
    <table class="table">
      <colgroup>
        <col style="width: 80%" />
        <col style="width: 20%" />
      </colgroup>
      <thead class="table-dark">
        <tr>
          <td>
            <strong>Przedmiot</strong>
          </td>
          <td>
            <div class="table-second-column">
              <strong>ECTS</strong>
            </div>
          </td>
        </tr>
      </thead>
      <SimpleSummary
        summaryType="Grupy, w których jesteś"
        :summaryData="enrolledSummary"
      />
      <SimpleSummary
        summaryType="Grupy, do których czekasz w kolejce"
        :summaryData="enqueuedSummary"
      />
      <SimpleSummary
        summaryType="Grupy, które masz przypięte"
        :summaryData="pinnedSummary"
      />
      <SimpleSummary
        summaryType="Grupy, które masz zaznaczone"
        :summaryData="selectedSummary"
      />
      <tfoot class="table-dark">
        <tr>
          <td>
            <strong>Punktów ECTS łącznie:</strong>
          </td>
          <td>
            <div class="table-second-column">
              {{ getTotalPointsFromAllCategories() }}
            </div>
          </td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>

<style>
.table-second-column {
  width: 30%;
  text-align: right;
}
</style>
