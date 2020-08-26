// Instantiates timetable component.
//
// The timetable app assumes that DOM has an element of id #timetable. It also
// reads information about the groups that should be displayed from <script
// type="application/json"></script> element. The data is expected to be a list
// of GroupJSON objects as defined in `models.ts`.

import Vue from "vue";
import SimpleTimetable from "./components/SimpleTimetable.vue";
import { Group } from "./models";

Vue.config.productionTip = false;

new Vue({
  el: "#timetable",
  components: { SimpleTimetable },
  data: {
    groups: [],
  },
  render: function (h) {
    return h(SimpleTimetable, {
      props: {
        groups: this.groups,
      },
    });
  },
  created: function () {
    this.update_groups();
  },
  methods: {
    update_groups: function () {
      const groupsDump = JSON.parse(
        document.getElementById("timetable-data").innerHTML
      );
      for (const groupDump of groupsDump) {
        this.groups.push(new Group(groupDump));
      }
    },
  },
});
