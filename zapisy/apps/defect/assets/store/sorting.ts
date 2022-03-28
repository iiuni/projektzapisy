import { property } from "lodash";
import { DefectInfo } from "@/defect/assets/models";

interface State {
  property: string;
  order: boolean;
}
const state: State = {
  property: "last_modification",
  order: false,
};

const getters = {
  // compare compares two defects based on current sorter
  compare: (state: State) => (a: DefectInfo, b: DefectInfo) => {
    if (state.property == "modified") state.property = "last_modification";
    let propGetter = property(state.property) as (c: DefectInfo) => string;
    return state.order
      ? propGetter(a).localeCompare(propGetter(b))
      : propGetter(b).localeCompare(propGetter(a));
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
