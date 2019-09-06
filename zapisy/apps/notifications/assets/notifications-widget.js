import Vue from "vue";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faBell as fasBell } from "@fortawesome/free-solid-svg-icons/faBell";
import { faBell as farBell } from "@fortawesome/free-regular-svg-icons/faBell";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";

import Widget from "./components/Widget.vue";

library.add(fasBell, farBell);

Vue.component("font-awesome-icon", FontAwesomeIcon);

let notifications_app = new Vue({
    el: "#notificationswidget",
    components: {
        Widget
    },
    render: function(h) {
        return h(Widget);
    }
});
