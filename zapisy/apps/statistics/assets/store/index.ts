import { createStore } from "vuex";

import courses from "./courses";
import filters from "./filters";
import sorting from "./sorting";

export default createStore({
  modules: {
    courses,
    filters,
    sorting,
  },
});
