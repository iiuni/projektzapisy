// Module filters implements the registration and current state of course
// filters.
import { every, invokeMap, values } from "lodash";

import { ActionContext } from "vuex";
import { CourseInfo } from "./courses";

export interface Filter {
    visible(c: CourseInfo): boolean;
}

interface State {
    filters: { [id: string]: Filter };
}
const state: State = {
    filters: {}
};

const getters = {
    // visible runs all the registered filters on the given course.
    visible: (state: State) => (c: CourseInfo) => {
        return every(invokeMap(values(state.filters), "visible", c));
    }
};

const mutations = {
    // registerFilter can be also used to update filter data.
    registerFilter(state: State, { k, f }: { k: string, f: Filter }) {
        state.filters[k] = f;
    }
};

const actions = {};

export default {
    namespaced: true,
    state,
    getters,
    actions,
    mutations
};
