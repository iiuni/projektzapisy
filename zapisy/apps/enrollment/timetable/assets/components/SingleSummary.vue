<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { DayOfWeek, nameDay, Group, Course, Term } from "../models";

export class CourseWithGroups extends Course {
  public groups: Group[];
  public isRepeated: Boolean;

  constructor(
    public course: Course,
    public courseGroups: Group[],
    public courseIsRepeated: Boolean
  ) {
    super(course.id, course.name, course.shortName, course.url, course.points);
    this.groups = courseGroups;
    this.isRepeated = courseIsRepeated;
  }
}

const SingleSummaryProps = Vue.extend({
  props: {
    summaryType: {
      type: String,
      default: "",
    },
    summaryData: {
      type: Array as () => Array<CourseWithGroups>,
      default() {
        return [];
      },
    },
  },
});

@Component({})
export default class SingleSummary extends SingleSummaryProps {
  expandedCourses: { [cid: number]: boolean } = {};
  expandedCategory: Boolean = false;

  public getNameDay(day: DayOfWeek) {
    return nameDay(day).toLowerCase();
  }

  public getPrintablePoints(data: CourseWithGroups): String {
    return data.isRepeated ? "–" : String(data.points);
  }

  public getPrintableComma(idx: number, terms: Array<Term>): String {
    return terms.length == idx + 1 ? "" : "|";
  }

  public getTotalPoints(): Number {
    let sum = 0;
    this.summaryData.forEach((data) => {
      sum += data.isRepeated ? 0 : data.points;
    });
    return sum;
  }

  public toggleCourseView(cid: number) {
    if (this.expandedCourses[cid] === undefined) {
      Vue.set(this.expandedCourses, cid, true);
    } else {
      Vue.set(this.expandedCourses, cid, !this.expandedCourses[cid]);
    }
  }

  public isCourseViewOpened(cid: number): boolean {
    return this.expandedCourses[cid] === undefined
      ? false
      : this.expandedCourses[cid];
  }

  public toggleCategoryView(): Boolean {
    this.expandedCategory = !this.expandedCategory;
    return this.expandedCategory;
  }
}
</script>

<template>
  <tbody>
    <tr class="table-default" v-if="summaryData.length > 0">
      <td class="summaryHeader" @click="toggleCategoryView()">
        <strong>{{ summaryType }}</strong>
      </td>
      <td class="summaryHeaderEcts">
        <div class="table-second-column">
          {{ getTotalPoints() }}
        </div>
      </td>
    </tr>
    <template v-if="expandedCategory">
      <template v-for="item in summaryData">
        <tr class="table-transparent" :key="item.id">
          <td @click="toggleCourseView(item.id)" class="table-transparent-data">
            <a @click="toggleCourseView(item.id)" :href="item.url">
              {{ item.name }}
            </a>
          </td>
          <td class="table-transparent-data">
            <div class="table-second-column">
              {{ getPrintablePoints(item) }}
            </div>
          </td>
        </tr>
        <tr v-if="isCourseViewOpened(item.id)" :key="item.name + item.id">
          <td class="p-2">
            <ul>
              <li v-for="group in item.groups" :key="group.id">
                <span class="type">{{ group.type.toLowerCase() }}:</span>
                <span
                  v-for="(term, idx) in group.terms"
                  class="term"
                  :key="idx"
                >
                  {{ getNameDay(term.weekday) }}
                  {{ term.startTimeString }}-{{ term.endTimeString }}
                  sala:
                  {{ term.classrooms }}
                  {{ getPrintableComma(idx, group.terms) }}
                </span>
              </li>
            </ul>
          </td>
        </tr>
      </template>
    </template>
  </tbody>
</template>

<style>
.table-transparent {
  background-color: rgba(0, 0, 0, 0.05);
}
.table-transparent-data {
  border-bottom: 1px solid #dee2e6;
}
.table-second-column {
  width: 30%;
  text-align: right;
}
</style>
