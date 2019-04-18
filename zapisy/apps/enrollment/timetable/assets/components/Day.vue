<script lang="ts">
// The base Day component. It is responsible for displaying a single weekday on
// the timetable.
//
// The most important task is to display terms (which represent a single meeting
// of a course group). The day component does also display a grid of hour rules
// (every half hour), hour labels on the left, and the day label at the top.
//
// The fitting of terms in the day component is solved with CSS grid. While not
// a perfect solution, it requires no algorithm, that would be difficult to
// maintain in our codebase.
import { range } from "lodash";
import Component from "vue-class-component";
import Vue from "vue";
import { Term, DayOfWeek, nameDay } from "../models";
import TermComponent from "./Term.vue";

interface DayData {
  key: string;
  d: DayOfWeek;
  dayName: string;
  terms: Array<Term>;
}

const DayProps = Vue.extend({
  props: {
    d: Number as () => DayOfWeek,
    terms: Array as () => Array<Term>,
  }
});

@Component({
  components: {
    Term: TermComponent
  }
})
export default class DayComponent extends DayProps {

  // Monday will always have hour labels shown on the left side.
  isMonday: boolean = this.d === DayOfWeek.Monday;

  dayName: string = nameDay(this.d)

  // In which column to put the day wrapper
  dayStyle = {
    gridColumn: this.d,
  };

  // For every full hour we have a label with it on the left side of the
  // timetable.
  get hourLabels() {
    return [...Array(16).keys()].map(k => ({
      key: "hour-label-" + k,
      hour: k + 8 + ":00",
      style: {
        gridRow: k * 4 + 2 + "/" + (k * 4 + 2)
      }
    }));
  }

  // Horizontal rules with alternating solid/dotted style will be drawn
  // every half hour.
  get halfHourRules() {
    return range(0, 61, 2).map(k => ({
      key: `hour-rule-${k}`,
      style: {
        gridRow: `${k+3} / ${k+3}`,
        borderTopStyle: k % 4 === 0 ? "solid" : "dotted",
      }
    }));
  }
}
</script>

<template>
  <div class='day' :class="{monday: isMonday}" :style="dayStyle">
    <span class="day-label">{{ dayName }}</span>

    <div class="hour-label" v-for="h of hourLabels" :style="h.style" :key="h.key">
      <span>{{ h.hour }}</span>
    </div>

    <template v-for="r of halfHourRules">
      <div class="gridline-row" :key="r.key" :style="r.style" ></div>
    </template>

    <div class="day-wrapper">

      <template v-for="t of terms">
        <Term :key="t.id" :term="t" />
      </template>
    </div>
  </div>
</template>


<style lang="scss" scoped>
.day {
  margin-bottom: 3rem;
  grid-template-columns: 0 1fr;
  // First row is for week-day label. Then we have a row for every quarter-hour
  // between 8:00 and 23:00.
  grid-template-rows: 25px repeat(61, 8px);

  display: grid;
  // border: 1px solid #dddddd;
}

@media (max-width: 992px) {
  .day {
    // On a small screen we will always show the hour labels.
    grid-template-columns: 45px minmax(100px, 1fr);
    grid-column: 1/2 !important;
  }
}

// Monday will always have its hour labels displayed.
.monday .hour-label {
  visibility: inherit;
}

.day-wrapper {
  grid-column: 2;
  grid-row: 3 / 63;
  border: 1px solid #dddddd;

  display: grid;
  grid-template-rows: repeat(60, 8px);
  width: 1fx;
}

.day-label {
  grid-row: 1;
  grid-column: 2;
  text-align: center;
  padding-top: 5px;
}

.hour-label {
  grid-column: 1;
  display: inline-flex;
  flex-direction: row-reverse;

  @media (min-width: 992px) {
    visibility: hidden;
  }

  span {
    padding-right: 10px;
    vertical-align: middle;
  }
}

.gridline-row {
  grid-column: 2/3;
  border-top: 1px #dddddd;
  height: 0px;
}
</style>
