// This module implements a state of the prototype.
//
// The main purpose of the state is to know, which groups should be presented on
// the timetable, and what their status is. It will however also maintain the
// collections of downloaded groups that are not currently presented.

/// <reference types="node" />
import Vue from "vue";
import Vuex from "vuex";

import groups from "./groups";
import courses from "./courses";

Vue.use(Vuex);

const debug: boolean = process.env.NODE_ENV !== "production";

export default new Vuex.Store({
    modules: {
        groups,
        courses,
    },
    strict: debug,
});
