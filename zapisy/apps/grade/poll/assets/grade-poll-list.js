import Vue from "vue";

import GradePollList from "./components/GradePollList.vue";

document.addEventListener("DOMContentLoaded", () => {
  new Vue({
    el: "#course-sections",
    render: (h) =>
      h(GradePollList, {
        props: {
          polls: JSON.parse(document.getElementById("data-polls").innerHTML),
          submissionsCount: JSON.parse(
            document.getElementById("data-submissions-count").innerHTML
          ),
          currentPoll: JSON.parse(
            document.getElementById("data-current-poll").innerHTML
          ),
          isSuperuser: JSON.parse(
            document.getElementById("data-is-superuser").innerHTML
          ),
          selectedSemesterId: JSON.parse(
            document.getElementById("data-selected-semester").innerHTML
          ),
        },
      }),
  });
});
