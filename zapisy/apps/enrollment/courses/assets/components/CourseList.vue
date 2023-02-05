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
  const names: { [key: number]: string } = {
    5: "informatyczne 1",
    7: "informatyczne inż.",
    8: "obowiązkowe",
    9: "obowiązkowe",
    13: "projekty",
    14: "seminaria",
    15: "nieinformatyczne",
    35: "inne",
    36: "kursy 1",
    37: "kursy 2",
    38: "informatyczne 2",
    39: "informatyczne 2",
    40: "kursy inż.",
    41: "proseminaria",
    42: "humanistyczno-społeczne",
    43: "matematyczne",
  };

  const { courseType } = course;
  const groupName = names[courseType || 35];
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
    <span v-for="(g, i) in groups" v-bind:key="g.id">
      <div v-if="Object.keys(groups).length > 1" class="group">
        {{ i }}
      </div>

      <span v-for="c in g" v-bind:key="c.id">
        <li>
          <a :href="c.url" class="d-block px-4 py-1 text-decoration-none">
            {{ c.name }}
          </a>
        </li>
      </span>
    </span>
  </ul>
</template>

<style lang="scss" scoped>
.group {
  font-weight: 500;
  font-size: larger;
  margin: 5px;
  text-transform: capitalize;
  color: #212529;
}
</style>
