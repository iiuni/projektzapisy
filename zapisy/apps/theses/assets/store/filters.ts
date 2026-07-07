import { every, invokeMap, values } from "lodash";

import { ThesisInfo } from "./theses";

export interface Filter {
  //previously c: ThesisInfo. Now more universal.
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
  visible: (state: State) => (c: ThesisInfo) => {
    return every(invokeMap(values(state.filters), "visible", c));
  },
};

const mutations = {
  // registerFilter can be also used to update filter data.
  registerFilter(state: State, { k, f }: { k: string; f: Filter }) {
    state.filters[k] = f;
  },
  // clearFilter can be used to notify filters to reset their state.
  clearFilters(_: State) {
    // Intentionally left empty. No state change is required to notify
    // subscribers of 'filters/clearFilters' mutation.
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
