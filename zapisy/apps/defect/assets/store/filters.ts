import { every, invokeMap, values } from "lodash";
import { DefectInfo } from "@/defect/assets/models";

export interface Filter {
  visible(c: DefectInfo): boolean;
}

interface State {
  filters: { [id: string]: Filter };
}
const state: State = {
  filters: {},
};

const getters = {
  // visible runs all the registered filters on the given course.
  visible: (state: State) => (c: DefectInfo) => {
    return every(invokeMap(values(state.filters), "visible", c));
  },
};

const mutations = {
  // registerFilter can be also used to update filter data.
  registerFilter(state: State, { k, f }: { k: string; f: Filter }) {
    state.filters[k] = f;
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
