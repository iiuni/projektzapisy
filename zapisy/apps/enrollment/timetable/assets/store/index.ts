// This module implements a state of the prototype.
//
// The main purpose of the state is to know, which groups should be presented on
// the timetable, and what their status is. It will however also maintain the
// collections of downloaded groups that are not currently presented.
// import Vue from "vue";
// import Vuex from "vuex";
import {createStore} from 'vuex';

import courses from './courses';
import filters from './filters';
import groups from './groups';

// Vue.use(Vuex);

export default createStore({
  modules: {
    groups,
    courses,
    filters,
  },
});
