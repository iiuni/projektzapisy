// Module courses implements the logic of selecting courses. On the first
// selection, the course's groups are downloaded and managed by groups module.
import axios from "axios";
import { values, flatten, sortBy } from "lodash";
import { ActionContext } from "vuex";
import { GroupJSON, CourseShellJSON, Course, CourseShell } from "../models";
import store from ".";

// Sets header for all POST requests to enable CSRF protection.
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

interface State {
    name: string;
    semester: string;
    owner: string;
    effects: string[];
    types: string[];
    tags: string[];
}
const state: State = {
    name: "",
    semester: "",
    owner:"",
    effects: [],
    types: [],
    tags: [],
};
type FilterId = "name"|"semester"|"effects"|"tags"|"types"|"owner";
type FilterArrayId = "effects"|"tags"|"types";
const getters = {
    activeFilter(state:State){
        return (id:FilterArrayId)=>{
            console.log("got asked about:",id);
            if(id === "effects") return state.effects;
            if(id === "types") return state.types;
            if(id === "tags") return state.tags;
            console.error("had to anwser garbage!");
            return [];
        }
    },
    tester(state:State){
        return (course:CourseShell)=>{
            if(state.semester !== "" && course.semester !== state.semester) return false;
            if(state.name !== "" && !course.name.startsWith(state.name)) return false; 
            if(state.owner !== "" && course.owner !== state.owner) return false; 
            if(state.tags.length !== 0){
                if(!state.tags.reduce( (prev,curr)=>prev && course.tags.includes(curr) , true )) return false;
            }
            if(state.effects.length !== 0){
                if(!state.effects.reduce( (prev,curr)=>prev && course.effects.includes(curr) , true )) return false;
            }
            if(state.types.length !== 0){
                if(!state.types.reduce( (prev,curr)=>prev && course.type === curr , true )) return false;
            }
            return true;
        }
    },
	name(state:State):string {
		 return state.name;
	},
	owner(state:State):string {
		 return state.owner;
	},
	semester(state:State):string {
		 return state.semester;
	},
	effects(state:State):string[] {
		 return state.effects;
	},
    tags(state:State):string[] {
        return state.tags;
    },
    types(state:State):string[] {
        return state.types;
    },
};

const actions = {
    setFilter({ commit }: ActionContext<State, any>, [id,payload]:[string,string]) {
        commit("setFilter", [id,payload]);
    },
    updateFilter({ commit }: ActionContext<State, any>, [id,payload]:[FilterArrayId,string[]]) {
        console.info("triggering filters/updateFilter with",[id,payload]);
        commit("updateFilter", [id,payload]);
    },
    dropFilter({ commit }: ActionContext<State, any>, [id,payload]:[string,string]) {
        commit("dropFilter", [id,payload]);
    },
    clearFilter({ commit }: ActionContext<State, any>, id: string) {
        commit("clearFilter", id);
    },
};


const mutations = {
    setFilter(state: State, [filterId,filterValue]: [FilterId,string]) {
		let hook:string[];
		if(filterId === "name") state.name = filterValue;
		if(filterId === "owner") state.name = filterValue;
		if(filterId === "semester") state.semester = filterValue;
		if(filterId === "effects") hook = state.effects;
		if(filterId === "types") hook = state.types;
		if(filterId === "tags") hook = state.tags;
		hook.push(filterValue); // could add check for duplicates in case of time hazads
    },
    clearFilter(state: State, filterId: FilterId) {
        if(filterId === "name") state.name = "";
        if(filterId === "owner") state.owner = "";
        if(filterId === "effects") state.effects = [];
        if(filterId === "types") state.types = [];
        if(filterId === "tags") state.tags = [];
    },
    dropFilter(state: State, [filterId,filterValue]: [string,string]) {
        if(filterId === "name") {
			state.name = "";
			return;
		}
		else if(filterId === "effects"){
            state.effects = state.effects.filter( el => el !== filterValue);
        }
		else if(filterId === "types"){
            state.types = state.types.filter( el => el !== filterValue);
        }
		else if(filterId === "tags"){
            state.tags = state.tags.filter( el => el !== filterValue);
        }
    },
    updateFilter(state: State, [filterId,filterValue]: [FilterArrayId,string[]]) {
		if(filterId === "effects"){
            state.effects = filterValue;
        }
		else if(filterId === "types"){
            state.types = filterValue;
        }
		else if(filterId === "tags"){
            state.tags = filterValue;
        }
    },
    
};

export default {
    namespaced: true,
    getters,
    state,
    actions,
    mutations,
};
