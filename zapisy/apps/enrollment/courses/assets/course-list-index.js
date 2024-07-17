import { createApp } from "vue";
import { createStore } from "vuex";

import CourseList from "./components/CourseList.vue";
import CourseFilter from "../../timetable/assets/components/CourseFilter.vue";
import filters from "../../timetable/assets/store/filters";

const store = new createStore({
  modules: {
    filters,
  },
});

if (document.getElementById("course-filter") !== null) {
  const filterApp = createApp(CourseFilter);
  filterApp.use(store);
  filterApp.mount("#course-filter");
}

const courseApp = createApp(CourseList);
courseApp.use(store);
courseApp.mount("#course-list");
