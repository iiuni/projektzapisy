import Vue from "vue";

import GradePollList from "./components/GradePollList.vue";

document.addEventListener("DOMContentLoaded", () => {
  const courseSectionsElement = document.getElementById("course-sections");
  new Vue({
    el: "#course-sections",
    render: (h) =>
      h(GradePollList, {
        props: {
          polls: JSON.parse(courseSectionsElement.dataset.polls),
          submissionsCount: JSON.parse(
            courseSectionsElement.dataset.submissionsCount
          ),
          currentPoll: JSON.parse(courseSectionsElement.dataset.currentPoll),
          selectedSemesterId: JSON.parse(
            courseSectionsElement.dataset.selectedSemesterId
          ),
          isSuperuser: JSON.parse(courseSectionsElement.dataset.isSuperuser),
        },
      }),
  });
});
