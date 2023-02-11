<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "@/enrollment/timetable/assets/store/courses";

type GroupedCourses = { [key: string]: CourseInfo[] };

const defaultType = "?";
const typeNames: { [key: string]: string } = {
  O1: "obowiązkowe 1",
  O2: "obowiązkowe 2",
  O3: "obowiązkowe 3",
  Oinż: "obowiązkowe inż.",

  I1: "informatyczne 1",
  Iinż: "informatyczne inż.",
  I2: "informatyczne 2",
  "I2.T": "informatyczne 2",
  "I2.Z": "informatyczne 2",

  K1: "kursy 1",
  "K.inż": "kursy inż.",
  K2: "kursy 2",

  P: "projekty",

  PS: "proseminaria",
  S: "seminaria",

  N: "nieinformatyczne",

  HS: "humanistyczno-społeczne",

  [defaultType]: "inne",

  MAT: "matematyczne",
};

export default Vue.extend({
  data() {
    return {
      courses: [] as CourseInfo[],
      groupedCourses: {} as GroupedCourses,
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
    this.groupedCourses = reorder(
      this.visibleCourses.reduce(groupCoursesByType, {})
    );

    // Append the initial query string to links in the semester dropdown.
    updateSemesterLinks();

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.filter(this.tester);
          this.groupedCourses = reorder(
            this.visibleCourses.reduce(groupCoursesByType, {})
          );

          // Update the query string of links in the semester dropdown
          // to reflect the new state of filters.
          updateSemesterLinks();
          break;
      }
    });
  },
});

function groupCoursesByType(groups: GroupedCourses, course: CourseInfo) {
  const { courseTypeName } = course;
  const groupName =
    typeNames[courseTypeName || defaultType] || typeNames[defaultType];
  groups[groupName] = groups[groupName] || [];
  groups[groupName].push(course);
  return groups;
}

// Sorts groups by the order defined in `typeNames`
function reorder(groups: GroupedCourses) {
  const order = Object.values(typeNames);
  return order.reduce(
    (ordered, item) =>
      groups[item] ? { ...ordered, [item]: groups[item] } : { ...ordered },
    {}
  );
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
    <li v-for="(g, i) in groupedCourses" v-bind:key="g.id">
      <h5 class="my-2 text-capitalize">
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
