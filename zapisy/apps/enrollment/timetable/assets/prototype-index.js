// Instantiates Timetable prototype component.
//
// It will put the prototype component in the DOM element with id #timetable.
// Two sets of data is read — the description of all the courses, and the
// description of groups the student is enqueued/enrolled into. Two <script
// type="application/json"></script> elements are used for this, one with id
// #courses-list, the other with id #timetable-data. For details look into
// `store/{groups.ts, courses.ts}`.

import Vue from "vue";

import Prototype from "./components/Prototype.vue";
import CourseList from "./components/CourseList.vue";
import CourseFilter from "./components/CourseFilter.vue";
import store from "./store";

new Vue({ el: '#timetable', render: h => h(Prototype), store });
new Vue({ el: '#course-filter', render: h => h(CourseFilter), store });
new Vue({ el: '#course-list', render: h => h(CourseList), store });
