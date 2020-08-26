import Vue from "vue";
import ThesesList from "./components/ThesesList.vue";
import ThesisFilter from "./components/ThesisFilter.vue";
import store from "./store";

new Vue({
  el: "#theses-filter",
  components: {
    ThesisFilter,
  },
  render: function (h) {
    return h(ThesisFilter);
  },
  store,
});

new Vue({
  el: "#theses-list",
  components: {
    ThesesList,
  },
  render: function (h) {
    return h(ThesesList);
  },
  store,
});
