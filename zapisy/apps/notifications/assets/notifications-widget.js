import Vue from "vue";
import Widget from "./components/Widget.vue";
import store from "./store";

new Vue({
  el: "#notificationswidget",
  components: {
    Widget,
  },
  render: function (h) {
    return h(Widget);
  },
  store,
});
