import { values, sortBy } from "lodash";
import { ActionContext } from "vuex";
import { DefectInfo } from "@/defect/assets/models";

interface State {
  defects: DefectInfo[];
}
const state: State = {
  defects: [],
};

const getters = {
  defects(state: State): Array<DefectInfo> {
    return sortBy(values(state.defects), "title");
  },
};

const actions = {
  initFromJSONTag({ commit }: ActionContext<State, any>) {
    const defectsDump = JSON.parse(
      document.getElementById("defect-data")!.innerHTML
    ) as DefectInfo;
    commit("setDefects", defectsDump);
  },
};

const mutations = {
  setDefects(state: State, defects: DefectInfo[]) {
    defects.forEach((c, id) => {
      state.defects[id] = c;
    });
  },
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
