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

// Get the server field
const djangoField = document.getElementById("id_students");

// Replace it with the placeholder for the custom MultiSelectFilter
const multiselectPlaceholder = document.getElementById("student-filter");
djangoField.before(multiselectPlaceholder);
djangoField.style.display = "none";

// Create the custom MultiSelectFilter
new Vue({ el: "#student-filter", render: (h) => h(StudentFilter), store });
