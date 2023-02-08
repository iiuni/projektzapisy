import Vue from "vue";
import Widget from "./components/Widget.vue";

new Vue({
  el: "#notificationswidget",
  components: {
    Widget,
  },
  render: function (h) {
    return h(Widget);
  },
});
