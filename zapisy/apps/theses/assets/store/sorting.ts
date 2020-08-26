import { property } from "lodash";

import { ThesisInfo } from "./theses";

interface State {
  property: string;
  order: boolean;
}
const state: State = {
  property: "modified",
  order: false,
};

const getters = {
  // compare compares two theses based on current sorter
  compare: (state: State) => (a: ThesisInfo, b: ThesisInfo) => {
    if (state.property == "modified") {
      let propGetter = property(state.property) as (c: ThesisInfo) => number;
      return state.order
        ? propGetter(a) - propGetter(b)
        : propGetter(b) - propGetter(a);
    } else {
      let propGetter = property(state.property) as (c: ThesisInfo) => string;
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
