import Vue from "vue";

import GradePollList from "./components/GradePollList.vue";

document.addEventListener("DOMContentLoaded", () => {
  const courseSectionsElement = document.getElementById("course-sections");
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
          selectedSemesterId: JSON.parse(
            document.getElementById("data-selected-semester-id").innerHTML
          ),
          isSuperuser: JSON.parse(
            document.getElementById("data-is-superuser").innerHTML
          ),
        },
      }),
  });
});
