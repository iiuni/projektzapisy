import Vue from "vue";
import Vuex from "vuex";

import UserFilter from "./components/UserFilter.vue";
import UserList from "./components/UserList.vue";

Vue.use(Vuex);


new Vue({
        el: "#student-filter",
        render: h => h(UserFilter)
    });

new Vue({
        el: "#student-list",
        render: h => h(UserList)
    });
