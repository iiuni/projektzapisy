import Vue from "vue";

import UserFilter from "./components/UserFilter.vue";
import UserList from "./components/UserList.vue";


if (document.getElementById("user-filter") !== null) {
    new Vue({
        el: "#user-filter",
        render: h => h(UserFilter)
    });
}
if (document.getElementById("user-list") !== null) {
    new Vue({
        el: "#user-list",
        render: h => h(UserList)
    });
}
