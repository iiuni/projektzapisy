import { every, invokeMap, values } from "lodash";

import { CourseInfo } from "./courses";

export interface Filter {
  //previously c: CourseInfo. Now more universal.
  visible(c: any): boolean;
}

interface State {
  filters: { [id: string]: Filter };
}
const state: State = {
  filters: {},
};

const getters = {
  // visible runs all the registered filters on the given course.
  visible: (state: State) => (c: CourseInfo) => {
    return every(invokeMap(values(state.filters), "visible", c));
  },
};

const mutations = {
  // registerFilter can be also used to update filter data.
  registerFilter(state: State, { k, f }: { k: string; f: Filter }) {
    state.filters[k] = f;
  },
};

export default {
  namespaced: true,
  state,
  getters,
  mutations,
};
