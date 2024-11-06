import Vue from "vue";
import Vuex from "vuex";

import StudentFilter from "./components/StudentFilter.vue";
import filters from "@/enrollment/timetable/assets/store/filters";

Vue.use(Vuex);

const store = new Vuex.Store({
  modules: {
    filters,
  },
});

const djangoField = document.getElementById("id_students");
const multiselectPlaceholder = document.getElementById("student-filter");
djangoField.before(multiselectPlaceholder);
// element.style.display = "none";
// const data = djangoField.children;//.map(({ value, text }) => { value, text })
// console.log(data);

new Vue({ el: "#student-filter", render: (h) => h(StudentFilter), store });
