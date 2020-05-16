import Vue from "vue";
import ThesesList from "./components/ThesesList";
import ThesisFilter from "./components/ThesisFilter.vue";
import store from "./store";

let theses_filter_app = new Vue({
  el: "#theses-filter",
  components: {
    ThesisFilter
  },
  render: function(h) {
    return h(ThesisFilter);
  },
  store
});

let theses_list_app = new Vue({
  el: "#theses-list",
  components: {
    ThesesList
  },
  render: function(h) {
    return h(ThesesList);
  },
  store
});
