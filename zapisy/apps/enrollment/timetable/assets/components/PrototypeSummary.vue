<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import { Group } from "../models";
import SingleSummary from "./SingleSummary.vue";
import { CourseWithGroups } from "./SingleSummary.vue";

const PrototypeSummaryProps = Vue.extend({
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
    SingleSummary,
  },
})
export default class PrototypeSummary extends PrototypeSummaryProps {
  public getSummaryData(
    groupIncludeFilter: Function,
    groupOverrideFilter: Function
  ): CourseWithGroups[] {
    let includeGroups = this.groups.filter((g) => groupIncludeFilter(g));
    let includingCourses = new Set(includeGroups.map((g) => g.course.id));
    let overridingCourses = new Set(
      this.groups.filter((g) => groupOverrideFilter(g)).map((g) => g.course.id)
    );

    let summaryData: Array<CourseWithGroups> = [];
    for (let course of includingCourses) {
      let courseGroups = includeGroups.filter(
        (g) => !groupOverrideFilter(g) && g.course.id == course
      );

      if (courseGroups.length == 0) {
        continue;
      }

      let isCourseRepeating = overridingCourses.has(course);

      summaryData.push(
        new CourseWithGroups(
          courseGroups[0].course,
          courseGroups,
          isCourseRepeating
        )
      );
    }
    return summaryData;
  }

  public getTotalPointsFromAllCategories() {
    let courses = new Set(this.groups.map((g) => g.course.id));

    let sum = 0;
    this.groups.forEach((g) => {
      if (courses.has(g.course.id)) {
        sum += g.course.points;
        courses.delete(g.course.id);
      }
    });

    return sum;
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
      <SingleSummary
        summaryType="Grupy, w których jesteś"
        :summaryData="
          getSummaryData(
            (g) => g.isEnrolled,
            (g) => false
          )
        "
      />
      <SingleSummary
        summaryType="Grupy, do których czekasz w kolejce"
        :summaryData="
          getSummaryData(
            (g) => g.isEnqueued,
            (g) => g.isEnrolled
          )
        "
      />
      <SingleSummary
        summaryType="Grupy, które masz przypięte"
        :summaryData="
          getSummaryData(
            (g) => g.isPinned,
            (g) => g.isEnrolled || g.isEnqueued
          )
        "
      />
      <SingleSummary
        summaryType="Grupy, które masz zaznaczone"
        :summaryData="
          getSummaryData(
            (g) => g.isSelected,
            (g) => g.isEnrolled || g.isEnqueued || g.isPinned
          )
        "
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
