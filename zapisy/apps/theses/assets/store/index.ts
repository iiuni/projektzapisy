// import Vue from "vue";
// import Vuex from "vuex";
// import {createApp} from 'vue';
import { createStore } from "vuex";

import filters from "./filters";
import sorting from "./sorting";
import theses from "./theses";

export const store = createStore({
  modules: {
    theses,
    filters,
    sorting,
  },
});
// const app = createApp();
// Vue.use(Vuex);

// export default new Vuex.Store({
// });
