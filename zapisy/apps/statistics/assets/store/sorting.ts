import { property } from "lodash";

import { CourseInfo } from "./courses";

interface State {
  property: string;
  order: boolean;
}
const state: State = {
  property: "course_name",
  order: true,
};

const getters = {
  // compare compares two courses based on current sorter
  compare: (state: State) => (a: CourseInfo, b: CourseInfo) => {
    if (state.property == "max_of_waiting_students") {
      let propGetter = property(state.property) as (c: CourseInfo) => number;
      return state.order
        ? propGetter(a) - propGetter(b)
        : propGetter(b) - propGetter(a);
    } else {
      let propGetter = property(state.property) as (c: CourseInfo) => string;
      return state.order
        ? propGetter(a).localeCompare(propGetter(b))
        : propGetter(b).localeCompare(propGetter(a));
    }
  },
  getProperty: (state: State) => {
    return state.property;
  },
};

const mutations = {
  // changeSorting can be also used to update filter data.
  changeSorting(state: State, { k, f }: { k: string; f: boolean }) {
    state.property = k;
    state.order = f;
  },
};

const actions = {};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
