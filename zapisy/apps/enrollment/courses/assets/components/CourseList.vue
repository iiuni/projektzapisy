<script lang="ts">
// This particular CourseList component extends the functionality of other
// CourseList components by allowing the chosen filters to persist through
// changing semesters in the dropdown menu.
//
// It achieves this by using the UpdateSemesterLinks function to change
// the query string of the links.
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "@/enrollment/timetable/assets/store/courses";

// This component is used in the courses-course-list webpack
export default Vue.extend({
  data() {
    return {
      courses: [] as CourseInfo[],
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

    // Append the initial query string to links in the semester dropdown.
    updateSemesterLinks();

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleCourses = this.courses.filter(this.tester);
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
      <a :href="c.url" class="d-block px-4 py-1 text-decoration-none">{{
        c.name
      }}</a>
    </li>
  </ul>
</template>
