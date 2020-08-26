import Vue from "vue";
import TicketsGenerator from "./TicketsGenerator.vue";

Vue.config.productionTip = false;

window.onload = function () {
  new Vue({
    el: "#app",
    render: (h) => h(TicketsGenerator),
  });
};
