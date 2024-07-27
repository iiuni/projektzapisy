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
