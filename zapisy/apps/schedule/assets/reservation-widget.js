import Vue from "vue";
import ReservationEditor from "./components/ReservationEditor.vue";

function syncFormDisplay() {
  const formType = document.getElementById("form-type");
  const formCourse = document.getElementById("form-course");
  const formEvents = document.querySelectorAll(".form-event");

  if (
    !(formType instanceof HTMLSelectElement) ||
    !(formCourse instanceof HTMLElement)
  ) {
    return;
  }

  const isEvent = formType.value === "2";
  formCourse.classList.toggle("d-none", isEvent);
  formEvents.forEach((element) => {
    if (!(element instanceof HTMLElement)) {
      return;
    }
    element.classList.toggle("d-none", !isEvent);
  });
}

const mountElement = document.getElementById("reservation-editor");
const dataElement = document.getElementById("reservation-editor-data");

if (mountElement && dataElement) {
  const data = JSON.parse(dataElement.textContent || "{}");

  new Vue({
    el: "#reservation-editor",
    render: function (h) {
      return h(ReservationEditor, {
        props: {
          initialTerms: data.terms || [],
          initialFormsCount: data.initialFormsCount || 0,
          minNumForms: data.minNumForms || 1,
          maxNumForms: data.maxNumForms || 1000,
        },
      });
    },
  });
}

syncFormDisplay();

const formType = document.getElementById("form-type");
if (formType) {
  formType.addEventListener("change", syncFormDisplay);
}
