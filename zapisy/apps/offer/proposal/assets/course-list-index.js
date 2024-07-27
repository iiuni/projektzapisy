import { createApp } from "vue";
import { createStore } from "vuex";
import CourseList from "./components/CourseList.vue";
import CourseFilter from "./components/CourseFilter.vue";
import filters from "@/enrollment/timetable/assets/store/filters";

const store = createStore({
  modules: {
    filters,
  },
});

if (document.getElementById("course-filter") !== null) {
  const courseListApp = createApp(CourseFilter);
  courseListApp.use(store);
  courseListApp.mount("#course-filter");
}

if (document.getElementById("course-list") !== null) {
  const courseListApp = createApp(CourseList);
  courseListApp.use(store);
  courseListApp.mount("#course-list");
}
