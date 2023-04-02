import Vue from "vue";

import GradePollList from "./components/GradePollList.vue";


document.addEventListener("DOMContentLoaded", () => {
  const courseSectionsElement = document.getElementById("course-sections");
  console.log(courseSectionsElement.dataset);
  new Vue({
    el: "#course-sections",
    render: h =>
      h(GradePollList, {
        props: {
          polls: JSON.parse(courseSectionsElement.dataset.polls),
          pollsOwn: JSON.parse(courseSectionsElement.dataset.pollsOwn),
          submissionsCount: JSON.parse(courseSectionsElement.dataset.submissionsCount),
          currentPoll: JSON.parse(courseSectionsElement.dataset.currentPoll),
          selectedSemester: JSON.parse(courseSectionsElement.dataset.selectedSemester),
          isSuperuser: JSON.parse(courseSectionsElement.dataset.isSuperuser)
        },
      })
  });
});