<script setup lang="ts">
import { CourseInfo } from "@/enrollment/timetable/assets/store/courses";
import { onMounted } from "vue";

import { computed, ref } from "vue";
import { useStore } from "vuex";

const store = useStore();

const courses = ref<CourseInfo[]>([]);
const visibleCourses = ref<CourseInfo[]>([]);
const tester = computed(() => store.getters["filters/visible"]);

visibleCourses.value = courses.value.filter(tester.value);

onMounted(() => {
  // When mounted, load the list of courses from embedded JSON and apply initial filters
  // fetched from the query string.Property "visibleCourses" was accessed during render but
  const courseData = JSON.parse(
    document.getElementById("courses-data")!.innerHTML
  ) as CourseInfo[];
  courses.value = courseData;
  visibleCourses.value = courseData.filter(tester.value);

  // Append the initial query string to links in the semester dropdown.
  updateSemesterLinks();

  store.subscribe((mutation) => {
    switch (mutation.type) {
      case "filters/registerFilter":
        visibleCourses.value = courses.value.filter(tester.value);
        // Update the query string of links in the semester dropdown
        // to reflect the new state of filters.
        updateSemesterLinks();
        break;
    }
  });
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
