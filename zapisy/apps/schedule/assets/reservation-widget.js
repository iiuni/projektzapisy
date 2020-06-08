import Vue from "vue";
import ClassroomPicker from "./components/ClassroomPicker.vue";

let schedule_reservation_widget_app = new Vue({
  el: "#reservation-widget",
  components: {
    ClassroomPicker,
  },
  render: function (h) {
    return h(ClassroomPicker);
  },
});
