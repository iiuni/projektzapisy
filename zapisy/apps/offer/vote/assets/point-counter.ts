// // This script sets-up a counter component at the top of Vote form page and
// // takes care of highlighting rows where the vote has been given out.

// import Vue from "vue";
// import Vuex from "vuex";

// import CounterComponent from "./components/CounterComponent.vue";
// import FilterComponent from "./components/CourseFilter.vue";

// import filters from "@/enrollment/timetable/assets/store/filters";

// // comp will hold a Vue component.
// let counterComponent: CounterComponent | null = null;

// var coursesDataStr: string;
// var coursesDataArray: Array<object>;

// // Given a name-value map and an input DOM element updates the value
// // corresponding to the input.
// function setValueMapFromInput(
//   map: { [key: string]: number },
//   input: HTMLInputElement
// ) {
//   const name: string = input.getAttribute("name")!;
//   const val: number = parseInt(input.value, 10);
//   map[name] = val;
// }

// // Given a <select> element highlights a table row containing it, if its
// value
// // is not a minimum option and removes highlight if it is.
// //
// // If the value is minimum available, but not 0 (which means the user is now
// in
// // correction and had voted for the course in the primary voting, we put a
// // colour on the course).
// function highlightVotedRow(select: HTMLSelectElement) {
//   let tableRow = select.closest("tr")!;
//   if (select.value !== select.options[0].text) {
//     tableRow.classList.remove("table-success");
//     tableRow.classList.add("table-primary");
//   } else if (select.value !== "0") {
//     tableRow.classList.add("table-success");
//     tableRow.classList.remove("table-primary");
//   } else {
//     tableRow.classList.remove("table-success");
//     tableRow.classList.remove("table-primary");
//   }
// }

// function setUpFilters() {
//   Vue.use(Vuex);

//   const store = new Vuex.Store({
//     modules: {
//       filters,
//     },
//   });

//   new Vue({
//     el: "#course-filter",
//     render: (h) => h(FilterComponent, { props: { refreshFun: applyFilters }
//     }), store,
//   });
// }

// function setUpCounter() {
//   const limit = parseInt(
//     document.getElementById("point-counter")!.innerHTML,
//     10
//   );
//   const inputs = document.querySelectorAll(".limit select");

//   // For every input (under class .limit) we store its value in inputsMap.
//   let inputsMap: { [key: string]: number } = {};
//   for (const input of inputs) {
//     setValueMapFromInput(inputsMap, input as HTMLInputElement);
//   }

//   counterComponent = new Vue({
//     el: "#point-counter",
//     data: {
//       inputs: inputsMap,
//       limit: limit,
//     },
//     render: function (h) {
//       return h(CounterComponent, {
//         props: {
//           inputs: this.inputs,
//           limit: this.limit,
//         },
//       });
//     },
//   });
// }

// function applyFilters(tester: any) {
//   const rows = document.querySelectorAll("tr");
//   const filtered: any = coursesDataArray.filter(tester);

//   for (const row of rows) {
//     let hideRow = true;
//     for (const courseIdx in filtered) {
//       if (row!.classList.contains("subject-id-" + filtered[courseIdx].id)) {
//         hideRow = false;
//         break;
//       }
//     }
//     if (hideRow) {
//       row!.classList.add("hidden");
//       row.setAttribute("style", "display: none;");
//     } else {
//       row!.classList.remove("hidden");
//       row.setAttribute("style", "");
//     }
//   }
// }

// function FormatCoursesData(coursesDataStr: string) {
//   return JSON.parse(coursesDataStr);
// }

// document.addEventListener("DOMContentLoaded", function () {
//   // We set-up the counter component in the beginning.
//   setUpCounter();
//   setUpFilters();
//   coursesDataStr = document.getElementById("courses-data")!.innerHTML;
//   coursesDataArray = FormatCoursesData(coursesDataStr);

//   const inputs = document.querySelectorAll(".limit select");

//   // Highlight "voted for" proposals ones where the current value is not a
//   // minimum option.
//   for (const input of inputs) {
//     highlightVotedRow(input as HTMLSelectElement);
//   }

//   // Whenever one of the inputs is changed, we need to update the value
//   stored
//   // in the component.

//   for (const input of inputs) {
//     (input as HTMLElement).addEventListener("input", function (_) {
//       const row = this.closest("tr");

//       if (row!.classList.contains("limit")) {
//         // Update the map.
//         setValueMapFromInput(
//           counterComponent!.inputs,
//           this as HTMLInputElement
//         );
//       }

//       // If the value is different than minimum, add a highlight.
//       highlightVotedRow(this as HTMLSelectElement);
//     });
//   }
// });
