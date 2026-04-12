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
    const semester_dropdown = document.getElementById("semester-dropdown-menu");
    if (semester_dropdown !== null) {
      semester_dropdown.addEventListener("click", async (event) => {
        if (event.target.closest(".semester-link")) {
          event.preventDefault();
          const targetUrl = event.target.getAttribute("href");
          await this.fetch_new_groups(targetUrl);
          this.update_groups();
        }
      }, true);
    }
  },
  methods: {
    update_groups: function () {
      this.groups = [];
      const groupsDump = JSON.parse(
        document.getElementById("timetable-data").innerHTML
      );
      for (const groupDump of groupsDump) {
        this.groups.push(new Group(groupDump));
      }
    },
    fetch_new_groups: async function (url) {
      const response = await fetch(url);
      if (!response.ok){
        return;
      }
      const html = await response.text();
      const parser = new DOMParser();
      const DOMData = parser.parseFromString(html, "text/html");
      const timetableData = DOMData.getElementById("timetable-data").innerHTML;
      const dropdownTitle = DOMData.getElementById("semester-dropdown-title").innerText;
      document.getElementById("timetable-data").innerHTML = timetableData;
      document.getElementById("semester-dropdown-title").innerText = dropdownTitle;
    }
  },
});
