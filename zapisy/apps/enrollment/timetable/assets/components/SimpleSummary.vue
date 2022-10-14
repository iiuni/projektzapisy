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
  opened: Array<number> = [];

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

  public toggleView(cid: number) {
    let index = this.opened.indexOf(cid);
    if (index > -1) {
      this.opened.splice(index, 1);
    } else {
      this.opened.push(cid);
    }
  }

  public isViewOpened(cid: number) {
    return this.opened.includes(cid);
  }
}
</script>

<template>
  <tbody>
    <tr class="table-default" v-if="summaryData.length > 0">
      <td class="summaryHeader">
        <strong>{{ summaryType }}</strong>
      </td>
      <td class="summaryHeaderEcts">{{ getTotalPoints() }}</td>
    </tr>
    <template v-for="item in summaryData">
      <tr class="table-transparent" :key="item.id">
        <td
          @click="toggleView(item.id)"
          class="table-transparent-data"
          scope="col"
        >
          <a @click="toggleView(item.id)" :href="item.url">
            {{ item.name }}
          </a>
        </td>
        <td class="table-transparent-data">
          {{ getPoints(item) }}
        </td>
      </tr>
      <tr v-if="isViewOpened(item.id)" :key="item.name + item.id">
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
</style>
