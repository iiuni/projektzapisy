import { createApp } from "vue";
import ClassroomPicker from "./components/ClassroomPicker.vue";

if (document.getElementById("reservation-widget") !== null) {
  const app = createApp(ClassroomPicker);
  app.mount("#reservation-widget");
}
