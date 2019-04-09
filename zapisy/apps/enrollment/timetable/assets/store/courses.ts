// Module courses implements the logic of selecting courses. On the first
// selection, the course's groups are downloaded and managed by groups module.
import axios from "axios";
import { values, flatten, sortBy } from "lodash";
import { ActionContext } from "vuex";
import { GroupJSON } from "../models";

// Sets header for all POST requests to enable CSRF protection.
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

export interface FilterDetails {
    property:"entity__name"|"tags"|"effects"|"first_year"|"exam"|"seminars";
    value:string|boolean;
}



interface State {
    courses: { [id: number]: CourseShell };
    activeFilters: FilterDetails[];
    selection: number[];
    allTags: string[]
    allEffects: string[];
}
const state: State = {
    courses: {},
    selection: [],
    activeFilters: [],
    allEffects: [],
    allTags: [],
};

const getters = {
    courses(state: State): CourseShell[] {
        return sortBy(values(state.courses), "entity__name");
    },
    selection(state: State) {
        return state.selection;
    },
    activeFilters(state:State):FilterDetails[] {
        return state.activeFilters;
    },
    allEffects(state:State):string[] {
        return state.allEffects;
    },
    allTags(state:State):string[] {
        return state.allTags;
    },
};

const actions = {
    // updateSelection will fetch all the courses, for which we miss the data,
    // and then update the selection flags.
    updateSelection(context:ActionContext<State, any>, ids: number[]) {
        const { state, commit, dispatch } = context; 
        const idsToFetch = ids.filter(id => state.courses[id].groups === undefined);
        if(!idsToFetch.length) dispatch("commitSelection", ids);
        
        // This puts a lock on all the courses that will be fetched. That way we
        // avoid fetching the same course in parallel when the student is
        // clicking too fast.
        idsToFetch.forEach(c => commit("setGroupIDs", { c, ids: [] }));
        const requests = idsToFetch.map(id => axios.get(state.courses[id].url));
        axios.all(requests).then(axios.spread((...responses) => {
            responses.forEach((response, pos) => {
                const courseID = idsToFetch[pos];
                const groupsJSON = response.data as GroupJSON[];
                groupsJSON.forEach(groupJSON => {
                    commit("groups/updateGroup", { groupJSON }, { root: true });
                });
                const groupIDs = groupsJSON.map(g => g.id);
                commit("setGroupIDs", { c: courseID, ids: groupIDs });
            });
        })).then(() => dispatch("commitSelection", ids));

    },


    // Once all courses are downloaded, it updates the selection.
    commitSelection({ state, commit }: ActionContext<State, any>,
        ids: number[]) {
        commit("setSelection", ids);
        const selectedGroupIDs = flatten(ids.map(c =>
            state.courses[c].groups!));
        commit("groups/updateGroupSelection", selectedGroupIDs, { root: true });
    },

    // initFromJSONTag will be called at the start to populate the courses list.
    initFromJSONTag({ commit }: ActionContext<State, any>) {
        const coursesDump = JSON.parse(
            document.getElementById("courses-list")!.innerHTML
        ) as CourseShell[];
        commit("setCourses", coursesDump);
    },    // initFromJSONTag will be called at the start to populate the courses list.
    
    addFilter({ commit }: ActionContext<State, any>, filter: FilterDetails) {
        commit("addFilter", filter);
    },
    dropFilter({ commit }: ActionContext<State, any>, filter: FilterDetails) {
        commit("dropFilter", filter);
    },
};

const mutations = {
    setGroupIDs(state: State, { c, ids }: { c: number, ids: number[] }) {
        state.courses[c].groups = ids;
    },
    setCourses(state: State, courses: CourseShell[]) {
        const allEffects:string[] = [];
        const allTags:string[] = [];
        courses.forEach(c => {
            if(!c.effects) c.effects=[];
            c.effects
                .filter(e => !allEffects.includes(e))
                .forEach(e => allEffects.push(e));
            if(!c.tags) c.tags=[];
            c.tags
                .filter(e => !allTags.includes(e))
                .forEach(e => allTags.push(e));
            state.courses[c.id] = c;
        });
        state.allEffects = allEffects;
        state.allTags = allTags;
    },
    setSelection(state: State, ids: number[]) {
        state.selection = ids;
    },
    addFilter(state: State, filter: FilterDetails) {
        state.activeFilters.push(filter);
    },
    dropFilter(state: State, filter: FilterDetails) {
        state.activeFilters = state.activeFilters.filter( 
            tested => !(filter.property === tested.property && 
                        filter.value === tested.value) );
    },
    
};

export default {
    namespaced: true,
    getters,
    state,
    actions,
    mutations,
};
