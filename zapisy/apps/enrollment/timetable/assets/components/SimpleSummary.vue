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
    return nameDay(day).toLowerCase();
  }
  public objectLength(o: Object) {
    return Object.keys(o).length;
  }
}
</script>

<template>
  <div>
    <tbody v-if="objectLength(courses) > 0">
      <tr>
        <td class="summaryHeader">
          <strong>Suma punktów ECTS za {{ summaryType }}:</strong>
        </td>
        <td class="summaryHeaderEcts">{{ points }}</td>
      </tr>
    </tbody>
    <tbody v-for="(item, idx) in courses" :value="item" :key="idx">
      <tr class="courseHeader">
        <td class="name" scope="col">
          <a :href="item.url">
            {{ item.name }}
          </a>
        </td>
        <td
          v-if="item.summaryPoints !== -1"
          rowspan="2"
          class="ects"
          align="right"
        >
          {{ item.summaryPoints }}
        </td>
        <td v-else rowspan="2" class="ects" align="right">-</td>
      </tr>
      <tr class="courseDetails">
        <td class="courseDetails">
          <ul v-for="(group, gid) in groups" :value="group" :key="gid">
            <li v-if="groupsCondition(group, item)">
              <span class="type">{{ group.type.toLowerCase() }}:</span>
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
td.summaryHeader {
  background-color: white;
}
td.summaryHeaderEcts {
  text-align: right;
  background-color: white;
}
</style>
