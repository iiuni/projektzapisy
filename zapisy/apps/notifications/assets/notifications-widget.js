import { createApp } from "vue";
import Widget from "./components/Widget.vue";

if (document.getElementById("notificationswidget") !== null) {
  const app = createApp(Widget);
  app.mount("#notificationswidget");
}
