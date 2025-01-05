<script lang="ts">
// This particular CourseList component extends the functionality of other
// CourseList components by allowing for distinction between the courses
// in offer, in vote and withdrawn.
//
// It achieves this by extending the CourseInfo interface into the ProposalInfo
// interface with an appropriate property.
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "../../../../enrollment/timetable/assets/store/courses";

interface ProposalInfo extends CourseInfo {
  status: "IN_OFFER" | "IN_VOTE" | "WITHDRAWN";
}

// This component is used in the proposal-course-list webpack
export default Vue.extend({
  data() {
    return {
      courses: [] as ProposalInfo[],
      visibleCourses: [] as ProposalInfo[],
    };
  },
  computed: {
    ...mapGetters("filters", {
      tester: "visible",
    }),
  },
  mounted() {
    // When mounted, load the list of courses from embedded JSON and apply initial filters
    // fetched from the query string.
    const courseData = JSON.parse(
      document.getElementById("courses-data")!.innerHTML
    ) as ProposalInfo[];
    this.courses = courseData;
    this.visibleCourses = courseData.filter(this.tester);

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.filter(this.tester);
          break;
      }
    });
  },
});
</script>

<template>
  <div>
    <ul>
      <li
        v-for="c in visibleCourses"
        v-bind:key="c.id"
        class="mb-1"
        v-bind:class="c.status.toLowerCase()"
      >
        <a :href="c.url">{{ c.name }}</a>
      </li>
    </ul>

    <ul id="proposal-legend" class="text-muted">
      <li class="in_vote">Przedmiot poddany pod głosowanie w tym cyklu.</li>
      <li class="in_offer">Przedmiot w ofercie ale nie w tym cyklu.</li>
      <li class="withdrawn">Przedmiot wycofany z oferty (zarchiwizowany).</li>
    </ul>
  </div>
</template>

<style lang="scss" scoped>
// Defines clear colour-codes for the proposal list statuses.
//
// Refers to palette of Bootstrap 5.

.in_vote a {
  color: var(--bs-green);
}

.in_offer a {
  color: var(--bs-blue);
}

.withdrawn a {
  color: var(--bs-gray);
}

#proposal-legend {
  li {
    list-style: none;
    &:before {
      content: "■";
      vertical-align: middle;
      display: inline-block;
      margin-top: -0.3em;
      font-size: 1.5em;
      margin-right: 4px;
      margin-left: -17px;
    }
    &.in_vote:before {
      color: var(--bs-green);
    }

    &.in_offer:before {
      color: var(--bs-blue);
    }

    &.withdrawn:before {
      color: var(--bs-gray);
    }
  }
}
</style>
