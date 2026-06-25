import Vue from "vue";
import ReservationEditor, { type Term } from "./components/ReservationEditor.vue";

interface ReservationEditorData {
  terms: Term[];
  initialFormsCount: number;
  minNumForms: number;
  maxNumForms: number;
}

function syncFormDisplay() {
  const formType = document.getElementById("form-type") as HTMLSelectElement;
  // Sprawdzmay czy edytujemy "wydarzenie" wtedy, muismy pokazac dodatkowe pola
  const isEvent = formType.value === "2";

  // Rendereujemy dodatkowepola w zaleznosci od typu wydarzenia
  const formCourse = document.getElementById("form-course")!;
  formCourse.classList.toggle("d-none", isEvent);
  document.querySelectorAll<HTMLElement>(".form-event").forEach((element) => {
    element.classList.toggle("d-none", !isEvent);
  });
}

const data = JSON.parse(
  document.getElementById("reservation-editor-data")!.textContent!
) as ReservationEditorData;

new Vue({
  el: "#reservation-editor",
  render(h) {
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

syncFormDisplay();
document
  .getElementById("form-type")!
  .addEventListener("change", syncFormDisplay);
