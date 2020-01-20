import Vue from "vue";
import Vuex from "vuex";

import UserFilter from "./components/UserFilter.vue";
import UserList from "./components/UserList.vue";

Vue.use(Vuex);

if (document.getElementById("student-filter") !== null) {
    new Vue({
        el: "#student-filter",
        render: h => h(UserFilter)
    });
}
if (document.getElementById("student-list") !== null) {
    new Vue({
        el: "#student-list",
        render: h => h(UserList)
    });
}
if (document.getElementById("employee-filter") !== null) {
    new Vue({
        el: "#employee-filter",
        render: h => h(UserFilter)
    });
}
if (document.getElementById("employee-list") !== null) {

    new Vue({
        el: "#employee-list",
        render: h => h(UserList)
    });
}