import { values, sortBy } from "lodash";
import { ActionContext } from "vuex";

export interface GroupInfo {
  id: number;
  teacher_name: string;
  type_name: string;
  limit: number;
  enrolled: number;
  queued: number;
  pinned: number;
  guaranteed_spots: [{ name: string; limit: number }];
  url: string;
}

export interface CourseInfo {
  id: number;
  course_name: string;
  groups: GroupInfo[];
  waiting_students: [{ name: string; number: string }];
  max_of_waiting_students: number;
}

interface State {
  courses: CourseInfo[];
}
const state: State = {
  courses: [],
};

const getters = {
  courses(state: State): Array<CourseInfo> {
    return sortBy(values(state.courses), "course_name");
  },
};

const actions = {
  initFromJSONTag({ commit }: ActionContext<State, any>) {
    const statisticsDump = JSON.parse(
      document.getElementById("statistics-data")!.innerHTML
    ) as CourseInfo;
    commit("setCoursesList", statisticsDump);
  },
};

const mutations = {
  setCoursesList(state: State, courses: CourseInfo[]) {
    courses.forEach((c, id) => {
      state.courses[id] = c;
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
