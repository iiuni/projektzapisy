// Module groups implements parts of the state concerned with remembering which
// groups should be presented on the timetable. It will maintain a store of
// groups data at hand and will download new data if necessary.
import axios from "axios";
import { keys, values, isEmpty, xor, find, isNil } from "lodash";
import Vue from "vue";
import { ActionContext } from "vuex";

import { Course, Group, GroupJSON } from "../models";

// Sets header for all POST requests to enable CSRF protection.
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

type GroupById = { [id: number]: Group };
type CourseById = { [id: number]: Course };

// Coalesce is a useful function that returns first defined value in the
// argument list, or undefined if there is none.
function coalesce(...args: Array<any | null | undefined>) {
  return find(args, (o) => !isNil(o));
}
let conditionGenerator = {
  selected: (g: GroupById, group: Group, c: number) =>
    g[1].isSelected && !g[1].isEnrolled && !g[1].isEnqueued && !g[1].isPinned && g[1].course.id === c && g[1].id !== group.id,
  enrolled: (g: GroupById, group: Group, c: number) =>
    g[1].isEnrolled && g[1].course.id === c && g[1].id !== group.id,
  enqueued: (g: GroupById, group: Group, c: number) =>
    g[1].isEnqueued && g[1].course.id === c && g[1].id !== group.id,
  pinned: (g: GroupById, group: Group, c: number) =>
    g[1].isPinned && g[1].course.id === c && g[1].id !== group.id,
};

function updateState(
  points: number,
  courses: CourseById,
  group: Group,
  threshold: number,
  condition: Function
) {
  let counter = 0;
  let c = group.course.id;
  Object.entries(state.store).forEach((g) => {
    if (condition(g, group, c)) {
      counter++;
    }
  });
  if (counter == threshold && courses[c] !== undefined) {
    points -= courses[c].points;
    delete courses[c];
  }
  return { points: points, courses: courses };
}

function initializeGroupInSummary(state: State, course: Course, group: Group) {
  if (group.isPinned && state.pinnedCourses[course.id] === undefined && state.enrolledCourses[course.id] === undefined && state.queuedCourses[course.id] === undefined) {
    group.course.summaryPoints = group.course.points
    state.pinnedCourses[group.course.id] = group.course;
    state.pinnedPoints += group.course.summaryPoints;
  }
  if (group.isSelected && state.selectedCourses[course.id] === undefined && state.pinnedCourses[course.id] === undefined && state.enrolledCourses[course.id] === undefined && state.queuedCourses[course.id] === undefined) {
    group.course.summaryPoints = group.course.points
    state.selectedCourses[group.course.id] = group.course;
    state.selectedPoints += group.course.summaryPoints;
  }
}

function lookForPinnedGroups(course: Course)
{
  Object.entries(state.store).forEach((g) => {
    if (g[1].course.id == course.id) {
      initializeGroupInSummary(state, course, g[1]);
    }
  });
}
// Store holds the data for all groups that are currently visible, but also for
// those, that had been visible.
interface State {
  store: GroupById;
  selectedPoints: number;
  queuedPoints: number;
  enrolledPoints: number;
  pinnedPoints: number;
  enrolledCourses: CourseById;
  queuedCourses: CourseById;
  pinnedCourses: CourseById;
  selectedCourses: CourseById;
}
const state: State = {
  store: {},
  selectedPoints: 0,
  queuedPoints: 0,
  enrolledPoints: 0,
  pinnedPoints: 0,
  enrolledCourses: {},
  queuedCourses: {},
  pinnedCourses: {},
  selectedCourses: {},
};

const getters = {
  // visibleGroups returns all the groups presented at the moment.
  visibleGroups(state: State) {
    return values(state.store).filter(
      (g) => g.isEnrolled || g.isEnqueued || g.isPinned || g.isSelected
    );
  },
};

const mutations = {
  setEnrolled(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isEnrolled = true;
    Vue.set(state.store, g.toString(), group);
  },
  unsetEnrolled(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isEnrolled = false;
    if (state.enrolledCourses[group.course.id] === undefined && state.pinnedCourses[group.course.id] !== undefined) {
      state.pinnedCourses[group.course.id].summaryPoints = state.pinnedCourses[group.course.id].points;
      state.pinnedPoints += state.pinnedCourses[group.course.id].summaryPoints;
    }
    Vue.set(state.store, g.toString(), group);
  },
  setEnqueued(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isEnqueued = true;
    Vue.set(state.store, g.toString(), group);
  },
  unsetEnqueued(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isEnqueued = false;
    if (state.queuedCourses[group.course.id] === undefined && state.pinnedCourses[group.course.id] !== undefined) {
      state.pinnedCourses[group.course.id].summaryPoints = state.pinnedCourses[group.course.id].points;
      state.pinnedPoints += state.pinnedCourses[group.course.id].summaryPoints;
    }
    Vue.set(state.store, g.toString(), group);
  },
  setPinned(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    let course: Course = group.course
    group.isPinned = true;
    initializeGroupInSummary(state, course, group);
    let updatedState = updateState(state.selectedPoints, state.selectedCourses, group, 0, conditionGenerator.selected);
    state.selectedCourses = updatedState.courses;
    state.selectedPoints = updatedState.points;
    if (state.selectedCourses[course.id] !== undefined) {
      state.selectedPoints -= state.selectedCourses[course.id].summaryPoints;  
      state.selectedCourses[group.course.id].summaryPoints = 0;
    }
    Vue.set(state.store, g.toString(), group);
  },
  unsetPinned(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isPinned = false;
    let updatedState = updateState(state.pinnedPoints, state.pinnedCourses, group, 0, conditionGenerator.pinned);
    state.pinnedCourses = updatedState.courses;
    state.pinnedPoints = updatedState.points;
    if (state.pinnedCourses[group.course.id] === undefined) {
      if (state.selectedCourses[group.course.id] !== undefined) {
        state.selectedCourses[group.course.id].summaryPoints = state.selectedCourses[group.course.id].points;
        state.selectedPoints += state.selectedCourses[group.course.id].summaryPoints;
      } else {
        initializeGroupInSummary(state, group.course, group);
      }
    }
    Vue.set(state.store, g.toString(), group);
  },
  setSelected(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isSelected = true;
    Vue.set(state.store, g.toString(), group);
  },
  unsetSelected(state: State, { g }: { g: number }) {
    let group: Group = state.store[g];
    group.isSelected = false;
    Vue.set(state.store, g.toString(), group);
  },
  // Updates the group data preserving the flags that are blank in the updated
  // data.
  updateGroup(state: State, { groupJSON }: { groupJSON: GroupJSON }) {
    let group = new Group(groupJSON);
    if (group.id in state.store) {
      const old = state.store[group.id];
      group.isSelected = old.isSelected;
      group.isEnrolled = coalesce(groupJSON.is_enrolled, old.isEnrolled);
      group.isEnqueued = coalesce(groupJSON.is_enqueued, old.isEnqueued);
      group.isPinned = coalesce(groupJSON.is_pinned, old.isPinned);
    } else {
      initializeGroupInSummary(state, group.course, group);
    }
    Vue.set(state.store, group.id.toString(), group);
  },
  // Flips the selection flag for the group whose selection changed.
  updateGroupSelection(state: State, ids: number[]) {
    const currentSelection = values(state.store)
      .filter((g) => g.isSelected)
      .map((g) => g.id);
      const flipSelection = xor(currentSelection, ids);
      flipSelection.forEach((id) => {
        let group = state.store[id];
        let course = group.course;
        // We will not show the group that is hidden.      
        group.isSelected = !group.isSelected;
        if (group.isSelected) {
          initializeGroupInSummary(state, course, group);
        } else {
          let updatedState = updateState(
            state.selectedPoints,
            state.selectedCourses,
            group,
            0,
            conditionGenerator.selected);
          state.selectedPoints = updatedState.points;
          state.selectedCourses = updatedState.courses;        
        }
        Vue.set(state.store, id.toString(), group);
    });
  },
};

const actions = {
  // These functions perform actions on a single group.
  pin({ commit }: ActionContext<State, any>, group: Group) {
    axios
      .post(group.actionURL, {
        action: "pin",
      })
      .then((_) => {
        commit("setPinned", { g: group.id });
      })
      .catch((reason) => {
        console.log("Pinning failed: ", reason);
      });
  },
  unpin({ commit }: ActionContext<State, any>, group: Group) {
    axios
      .post(group.actionURL, {
        action: "unpin",
      })
      .then((_) => {
        commit("unsetPinned", { g: group.id });
      })
      .catch((reason) => {
        console.log("Unpinning failed: ", reason);
      });
  },
  // When enqueue request is successful, the server will give back the list of
  // enqueued groups.
  enqueue({ commit }: ActionContext<State, any>, group: Group) {
    axios
      .post(group.actionURL, {
        action: "enqueue",
      })
      .then((_) => {
        commit("setEnqueued", { g: group.id });
      })
      .catch((reason) => {
        console.log("Enqueuing failed: ", reason);
      });
  },
  // When dequeue request is successful, the server will give back the list of
  // groups' ids, that we are removed from.
  dequeue({ commit }: ActionContext<State, any>, group: Group) {
    axios
      .post(group.actionURL, {
        action: "dequeue",
      })
      .then((_) => {
        commit("unsetEnrolled", { g: group.id });
        commit("unsetEnqueued", { g: group.id });
      })
      .catch((reason) => {
        console.log("Dequeuing failed: ", reason);
      });
  },

  // initFromJSONTag will be called at the beginning to set up the groups from
  // data provided in the JSON dump in DOM.
  initFromJSONTag({ commit }: ActionContext<State, any>) {
    const groupsDump = JSON.parse(
      document.getElementById("timetable-data")!.innerHTML
    ) as GroupJSON[];
    groupsDump.forEach((groupJSON) => {
      commit("updateGroup", { groupJSON });
    });
  },

  queryUpdatedGroupsStatus({ state, commit }: ActionContext<State, any>) {
    if (isEmpty(state.store)) {
      return;
    }
    const groupsToUpdate = keys(state.store);
    const updateURL: string = (
      document.getElementById("prototype-update-url") as HTMLInputElement
    ).value;
    axios
      .post(updateURL, groupsToUpdate)
      .then((response) => {
        const updatedGroups = response.data as GroupJSON[];
        updatedGroups.forEach((g: GroupJSON) => {          
          commit("updateGroup", { groupJSON: g });
        });
      })
      .catch((reason) => {
        console.log("Group info update failed: ", reason);
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
