<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "@/enrollment/timetable/assets/store/courses";

type CourseGroup = { [key: string]: CourseInfo[] };

export default Vue.extend({
  data() {
    return {
      courses: [] as CourseInfo[],
      groups: {} as CourseGroup,
      visibleCourses: [] as CourseInfo[],
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
    ) as CourseInfo[];
    this.courses = courseData;
    this.visibleCourses = courseData.filter(this.tester);
    this.groups = this.visibleCourses.reduce(groupCoursesByType, {});

    // Append the initial query string to links in the semester dropdown.
    updateSemesterLinks();

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.filter(this.tester);
          this.groups = this.visibleCourses.reduce(groupCoursesByType, {});

          // Update the query string of links in the semester dropdown
          // to reflect the new state of filters.
          updateSemesterLinks();
          break;
      }
    });
  },
});

function groupCoursesByType(group: CourseGroup, course: CourseInfo) {
  const defaultType = "?";
  const groupNames: { [key: string]: string } = {
    I1: "informatyczne 1",
    Iinż: "informatyczne inż.",
    O1: "obowiązkowe",
    O2: "obowiązkowe",
    P: "projekty",
    S: "seminaria",
    N: "nieinformatyczne",
    K1: "kursy 1",
    K2: "kursy 2",
    I2: "informatyczne 2",
    "I2.T": "informatyczne 2",
    "I2.Z": "informatyczne 2",
    "K.inż": "kursy inż.",
    PS: "proseminaria",
    HS: "humanistyczno-społeczne",
    MAT: "matematyczne",
    [defaultType]: "inne",
  };

  const { courseTypeName } = course;
  const groupName = groupNames[courseTypeName || defaultType];
  group[groupName] = group[groupName] || [];
  group[groupName].push(course);
  return group;
}

// Replaces the query string of links in the semester dropdown with the current query string.
function updateSemesterLinks() {
  const queryString = window.location.search;
  const semesterLinks = document.getElementsByClassName("semester-link");
  for (let i = 0; i < semesterLinks.length; i++) {
    const link: Element = semesterLinks[i];
    const hrefValue = link.getAttribute("href");
    if (hrefValue !== null) {
      const semesterPath = hrefValue.split("?")[0];
      link.setAttribute("href", semesterPath + queryString);
    }
  }
}
</script>

<template>
  <ul class="nav d-block">
    <li v-for="(g, i) in groups" v-bind:key="g.id">
      <h5 v-if="Object.keys(groups).length > 1" class="my-2 text-capitalize">
        {{ i }}
      </h5>

      <ul v-for="c in g" v-bind:key="c.id" class="list-unstyled">
        <li>
          <a :href="c.url" class="d-block px-4 py-1 text-decoration-none">
            {{ c.name }}
          </a>
        </li>
      </ul>
    </li>
  </ul>
</template>
