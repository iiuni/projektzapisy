import Vue from "vue";
import ClassroomPicker from "./components/ClassroomPicker.vue";

new Vue({
  el: "#reservation-widget",
  components: {
    ClassroomPicker,
  },
  render: function (h) {
    return h(ClassroomPicker);
  },
});
