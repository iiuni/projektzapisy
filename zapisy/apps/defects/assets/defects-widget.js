import Vue from "vue";
import DefectList from "./DefectList";
import DefectFilter from "./DefectFilter";
import store from "./store";

new Vue({
  el: "#defects-filter",
  components: {
    DefectFilter,
  },
  render: function (h) {
    return h(DefectFilter);
  },
  store,
});

new Vue({
  el: "#defects-list",
  components: {
    DefectList,
  },
  render: function (h) {
    return h(DefectList);
  },
  store,
});
