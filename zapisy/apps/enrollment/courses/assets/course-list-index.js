import Vue from "vue";
import Vuex from "vuex";

import CourseList from "./components/CourseList.vue";
import CourseFilter from "../../timetable/assets/components/CourseFilter.vue";
import filters from "../../timetable/assets/store/filters"

Vue.use(Vuex);

const store = new Vuex.Store({
    modules: {
        filters,
    }
});

if (document.getElementById("course-filter") !== null) {
    new Vue({ el: "#course-filter", render: h => h(CourseFilter), store });
}

new Vue({ el: "#course-list", render: h => h(CourseList), store });
