import { createApp } from "vue";

import UserFilter from "./components/UserFilter.vue";
import UserList from "./components/UserList.vue";

if (document.getElementById("user-filter") !== null) {
  const userFilterApp = createApp(UserFilter);
  userFilterApp.mount("#user-filter");
}
if (document.getElementById("user-list") !== null) {
  const userListApp = createApp(UserList);
  userListApp.mount("#user-list");
}
