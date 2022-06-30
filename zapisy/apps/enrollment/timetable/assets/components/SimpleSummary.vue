<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { DayOfWeek, nameDay, Group } from "../models";

const SimpleSummaryProps = Vue.extend({
  props: {
    summaryType: {
      type: String,
      default: "",
    },
    groups: {
      type: Array as () => Array<Group>,
      default: {},
    },
    groupsCondition: {
      type: Function,
    },
    courses: {
      type: Object,
      default: {},
    },
    points: {
      type: Number,
      default: 0,
    },
  },
});
@Component({})
export default class SimpleSummary extends SimpleSummaryProps {
  public GetNameDay(day: DayOfWeek) {
    return nameDay(day);
  }
}
</script>

<template>
  <div>
    <tbody>
      <tr>
        <td>
          <strong>Suma punktów ECTS za {{ summaryType }}:</strong>
        </td>
        <td class="ects">{{ points }}</td>
      </tr>
    </tbody>
    <tbody v-for="(item, idx) in courses" :value="item" :key="idx">
      <tr class="courseHeader">
        <td class="name" scope="col">
          <a href="{% url 'course-page' course.grouper.slug %}">
            {{ item.name }}
          </a>
        </td>
        <td rowspan="2" class="ects" align="right">
          {{ item.summaryPoints }}
        </td>
      </tr>
      <tr class="courseDetails">
        <td class="courseDetails">
          <ul v-for="(group, gid) in groups" :value="group" :key="gid">
            <li v-if="groupsCondition(group, item)">
              <span class="type">{{ group.type }}:</span>
              <span class="term">
                {{ GetNameDay(group.terms[0].weekday) }}
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
    </tbody>
  </div>
</template>

<style>
tbody {
  width: 114%;
  display: table;
}
td.courseDetails {
  width: 90%;
}
tr.simpleSumamry {
  width: 200%;
}
td.ects {
  text-align: right;
}
</style>
