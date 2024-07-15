<script setup lang="ts">
import { computed } from "vue";
import { range } from "lodash";
import { DayOfWeek, nameDay, Term } from "../models";
import TermComponent from "./Term.vue";
import TermControls from "./TermControls.vue";

// TODO fix typings in this file (style, key)
const props = defineProps({
  d: {
    type: Number,
    required: true,
  },
  terms: {
    type: Array,
    default: () => [],
  },
  isPrototype: {
    type: Boolean,
    default: false,
  },
});

// Monday will always have hour labels shown on the left side.
const isMonday = props.d === DayOfWeek.Monday;
const dayName = nameDay(props.d);
// In which column to put the day wrapper
const dayStyle = computed(() => ({ gridColumn: props.d }));
// For every full hour we have a label with it on the left side of the
// timetable.

const hourLabels = computed(() => {
  return [...Array(16).keys()].map((k) => ({
    key: "hour-label-" + k,
    hour: k + 8 + ":00",
    style: {
      gridRow: k * 4 + 2 + "/" + (k * 4 + 2),
    },
  }));
});

// Horizontal rules with alternating solid/dotted style will be drawn
// every half hour.
const halfHourRules = computed(() => {
  return range(0, 61, 2).map((k) => ({
    key: `hour-rule-${k}`,
    style: {
      gridRow: `${k + 3} / ${k + 3}`,
      borderTopStyle: k % 4 === 0 ? "solid" : "dotted",
    },
  }));
});
</script>

<template>
  <div class="day" :class="{ monday: isMonday }" :style="dayStyle">
    <span class="day-label">{{ dayName }}</span>

    <div
      class="hour-label"
      v-for="h of hourLabels"
      :style="h.style"
      :key="h.key"
    >
      <span>{{ h.hour }}</span>
    </div>

    <template v-for="r of halfHourRules">
      <div class="gridline-row" :key="r.key" :style="r.style"></div>
    </template>

    <div class="day-wrapper">
      <template v-for="t of terms">
        <TermControls :key="t.id" :term="t" v-if="isPrototype" />
        <TermComponent :key="t.id" :term="t" v-else />
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
