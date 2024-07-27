// Instantiates timetable component.
//
// The timetable app assumes that DOM has an element of id #timetable. It also
// reads information about the groups that should be displayed from <script
// type="application/json"></script> element. The data is expected to be a list
// of GroupJSON objects as defined in `models.ts`.

import SimpleTimetable from "./components/SimpleTimetable.vue";
import { Group } from "./models";
import { createApp } from "vue";

// Add comment -  This is removed in vue3
// Vue.config.productionTip = false;

if (
  document.getElementById("timetable-data") !== null &&
  document.getElementById("timetable") !== null
) {
  const groupsDump = JSON.parse(
    document.getElementById("timetable-data").innerHTML
  );
  const groups = groupsDump.map((groupDump) => new Group(groupDump));
  const timetableApp = createApp(SimpleTimetable, { groups });
  timetableApp.mount("#timetable");
}
