import Vue from "vue";
import Fullcalendar from "./components/Fullcalendar.vue";

new Vue({
  el: "#calendar",
  components: { Fullcalendar },
  render: (h) => h(Fullcalendar),
});
