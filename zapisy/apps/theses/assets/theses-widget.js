import { createApp } from "vue";
import ThesesList from "./components/ThesesList.vue";
import ThesisFilter from "./components/ThesisFilter.vue";
import { store } from "./store";

if (document.getElementById("theses-filter") !== null) {
  const thesesFilterApp = createApp(ThesisFilter);
  thesesFilterApp.use(store);
  thesesFilterApp.mount("#theses-filter");
}

if (document.getElementById("theses-list") !== null) {
  const thesesListApp = createApp(ThesesList);
  thesesListApp.use(store);
  thesesListApp.mount("#theses-list");
}
