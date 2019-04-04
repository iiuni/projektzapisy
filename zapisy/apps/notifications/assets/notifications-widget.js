
import Vue from "vue";
import Widget from "./components/Widget.vue";

let notifications_app = new Vue({
    el: "#notificationswidget",
    components: { Widget },
    data: {
        show: false,
    },
    render: function (h) {
        return h(Widget, {
            props: {
                show: this.show,
            }
        });
    },
}) 