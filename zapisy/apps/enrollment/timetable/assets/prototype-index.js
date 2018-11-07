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
import store from "./store";

Vue.config.productionTip = false

let timetable_app = new Vue({
    el: "#timetable",
    components: {
        Prototype,
    },
    store,
    render: h => { return h(Prototype); },
})