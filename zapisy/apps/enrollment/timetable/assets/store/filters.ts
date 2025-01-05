// Module filters implements the registration and current state of course
// filters.
import { every, invokeMap, values } from "lodash";

import { CourseInfo } from "./courses";

export interface Filter {
  visible(c: CourseInfo): boolean;
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
  // clearFilter can be used to notify filters to reset their state.
  clearFilters(_: State) {
    // Intentionally left empty. No state change is required to notify
    // subscribers of 'filters/clearFilters' mutation.
  },
};

const actions = {};

// When loading site tries to get last used filters from session.
// If there is no given key in session uses default filters.
// During first page load filters should be loaded
// from database to session if user is logged. (TODO: doesnt work until migration is done)
// After user logs in session preferences will be overriden by
// database preferences only if session preferences are empty (default filters).
export const LAST_FILTER_KEY = "last_searched_params";
export function getSearchParams() {
  const sessionSearchParams = sessionStorage.getItem(LAST_FILTER_KEY);
  return sessionSearchParams
    ? new URLSearchParams(sessionSearchParams)
    : new URL(window.location.href).searchParams;
}

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations,
};
