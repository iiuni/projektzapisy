import { values, sortBy } from "lodash";
import { ActionContext } from "vuex";

export interface ThesisInfo {
  id: number;
  title: string;
  is_available: boolean;
  kind: string;
  status: string;
  modified: number;
  has_been_accepted: boolean;
  advisor: string;
  advisor_last_name: string;
  url: string;
}

interface State {
  theses: ThesisInfo[];
}
const state: State = {
  theses: []
};

const getters = {
  theses(state: State): Array<ThesisInfo> {
    return sortBy(values(state.theses), "title");
  }
};

const actions = {
  initFromJSONTag({ commit }: ActionContext<State, any>) {
    const thesesDump = JSON.parse(
      document.getElementById("theses-data")!.innerHTML
    ) as ThesisInfo;
    commit("setTheses", thesesDump);
  }
};

const mutations = {
  setTheses(state: State, theses: ThesisInfo[]) {
    theses.forEach((c, id) => {
      state.theses[id] = c;
    });
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
