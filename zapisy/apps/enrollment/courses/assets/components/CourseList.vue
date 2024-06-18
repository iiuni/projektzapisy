<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "@/enrollment/timetable/assets/store/courses";

export default Vue.extend({
  data() {
    return {
      courses: [] as CourseInfo[],
      visibleCourses: [] as { courseInfo: CourseInfo; visible: boolean }[],
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
    this.visibleCourses = courseData.map((c) => ({
      courseInfo: c,
      visible: this.tester(c),
    }));

    // Append the initial query string to links in the semester dropdown.
    updateSemesterLinks();

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.map((c) => ({
            courseInfo: c,
            visible: this.tester(c),
          }));
          // Update the query string of links in the semester dropdown
          // to reflect the new state of filters.
          updateSemesterLinks();
          break;
      }
    });
  },
});

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
    <li v-for="c in visibleCourses" v-bind:key="c.id">
      <a
        :href="c.courseInfo.url"
        class="d-block px-4 py-1 text-decoration-none course-link"
        v-if="c.visible"
        >{{ c.courseInfo.name }}</a
      >
    </li>
  </ul>
</template>
