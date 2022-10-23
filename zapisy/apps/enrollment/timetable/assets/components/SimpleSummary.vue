<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { DayOfWeek, nameDay, Group, Course } from "../models";

export class CourseWithGroups extends Course {
  public groups: Group[];
  public isOverlapping: Boolean;

  constructor(
    public course: Course,
    public courseGroups: Group[],
    public courseIsOverlapping: Boolean
  ) {
    super(course.id, course.name, course.shortName, course.url, course.points);
    this.groups = courseGroups;
    this.isOverlapping = courseIsOverlapping;
  }
}

const SimpleSummaryProps = Vue.extend({
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
export default class SimpleSummary extends SimpleSummaryProps {
  openedCourses: Array<number> = [];
  openedCategory: Boolean = false;

  public getNameDay(day: DayOfWeek) {
    return nameDay(day).toLowerCase();
  }

  public getPoints(data: CourseWithGroups) {
    return data.isOverlapping ? "–" : data.points;
  }

  public getTotalPoints(): Number {
    let sum = 0;
    this.summaryData.forEach((data) => {
      sum += data.isOverlapping ? 0 : data.points;
    });
    return sum;
  }

  public toggleCourseView(cid: number) {
    let index = this.openedCourses.indexOf(cid);
    if (index > -1) {
      this.openedCourses.splice(index, 1);
    } else {
      this.openedCourses.push(cid);
    }
  }

  public isCourseViewOpened(cid: number) {
    return this.openedCourses.includes(cid);
  }

  public toggleCategoryView(): Boolean {
    this.openedCategory = !this.openedCategory;
    return this.openedCategory;
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
    <template v-for="item in summaryData">
      <tr v-if="openedCategory" class="table-transparent" :key="item.id">
        <td @click="toggleCourseView(item.id)" class="table-transparent-data">
          <a @click="toggleCourseView(item.id)" :href="item.url">
            {{ item.name }}
          </a>
        </td>
        <td class="table-transparent-data">
          <div class="table-second-column">
            {{ getPoints(item) }}
          </div>
        </td>
      </tr>
      <tr
        class=""
        v-if="openedCategory && isCourseViewOpened(item.id)"
        :key="item.name + item.id"
      >
        <td class="p-2">
          <ul v-for="group in item.groups" :key="group.id">
            <li>
              <span class="type">{{ group.type.toLowerCase() }}:</span>
              <span class="term">
                {{ getNameDay(group.terms[0].weekday) }}
                {{ group.terms[0].startTimeString }}-{{
                  group.terms[0].endTimeString
                }}
              </span>
              <span class="classroom"
                >sala:
                {{ group.terms[0].getClassrooms }}
              </span>
            </li>
          </ul>
        </td>
      </tr>
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
