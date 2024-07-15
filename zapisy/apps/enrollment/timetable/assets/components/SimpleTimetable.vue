<script setup lang="ts">
// SimpleTimemtable component is a base component for displaying timetable. It
// is responsible to extracting terms from the groups, distributing them among
// days and presenting the Day components for five weekdays.
//
// As for presentation, the days will be shown compactly (side-by-side) on
// computer screens, and one below another on small screens.
import { flatten, groupBy, range } from "lodash";
import Day from "./Day.vue";
import { Group, nameDay } from "../models";
import { computed } from "vue";

const props = defineProps({
  groups: {
    type: Array as () => Array<Group>,
    default: [],
  },
  isPrototype: {
    type: Boolean,
    default: false,
  },
});

// Populates timetable data to the day components. The terms are extracted
// from provided groups and distributed by their respective weekday.
const daysData = computed(() => {
  const groupTerms = props.groups.map((g) => g.terms);
  const allTerms = flatten(groupTerms);
  const terms_by_day = groupBy(allTerms, "weekday");

  return range(1, 6).map((d) => ({
    key: `day-${d}`,
    d: d,
    dayName: nameDay(d),
    terms: terms_by_day[d],
  }));
});
</script>

<template>
  <div class="week">
    <Day
      v-for="dd of daysData"
      :key="dd.key"
      :d="dd.d"
      :terms="dd.terms"
      :is-prototype="isPrototype"
    />
  </div>
</template>

<style lang="scss" scoped>
.week {
  margin: 0 auto;
  display: grid;
  // One column each for five days.
  grid-template-columns: repeat(5, 1fr);
  // We want a row for every quarter of an hour between 8:00 and 23:00.
  // (23 - 8) * 4 = 60. On top of that we will have a row for day labels.
}

@media (max-width: 992px) {
  .week {
    // On a small screen we prefer to show days one below another.
    grid-template-columns: 1fr;
  }
}
</style>
