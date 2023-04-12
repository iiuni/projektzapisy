import Vue from "vue";
import Vuex from "vuex";

import defects from "./defects";
import filters from "./filters";
import sorting from "./sorting";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    defects,
    filters,
    sorting,
  },
});
