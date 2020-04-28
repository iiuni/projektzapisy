import Vue from "vue";
import ReservationComponent from "./components/ReservationComponent.vue";

let schedule_reservation_widget_app = new Vue({
  el: "#reservation-widget",
  components: {
    ReservationComponent,
  },
  render: function (h) {
    return h(ReservationComponent);
  },
});
