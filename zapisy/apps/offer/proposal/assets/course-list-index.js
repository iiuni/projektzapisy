import Vue from "vue";
import Vuex from "vuex";

import CourseList from "./components/CourseList.vue";
import CourseFilter from "./components/CourseFilter.vue";
import filters from "@/enrollment/timetable/assets/store/filters"

Vue.use(Vuex);

const store = new Vuex.Store({
    modules: {
        filters,
    }
});

new Vue({ el: "#course-filter", render: h => h(CourseFilter), store });
new Vue({ el: "#course-list", render: h => h(CourseList), store });
