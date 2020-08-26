import Vue from "vue";
import Vuex from "vuex";

import theses from "./theses";
import filters from "./filters";
import sorting from "./sorting";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    theses,
    filters,
    sorting,
  },
});
