import Vue from "vue";
import Vuex from "vuex";

import notifications from "./notifications";

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    notifications,
  },
});
