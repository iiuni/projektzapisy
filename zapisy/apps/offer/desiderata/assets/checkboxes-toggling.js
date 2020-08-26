import { checkboxes } from "checkboxes.js/dist/jquery.checkboxes-1.2.2.js";

$.checkboxes = checkboxes;

// Enable range toggling.
$("table").checkboxes("range", true, "tr :checkbox");

// Enable row toggling.
$(".day-toggle").on("click", (e) => {
  e.preventDefault();
  const row = $(e.target).closest("tr");
  const checkboxes = row.find("[type='checkbox']").toArray();
  const state = checkboxes.some((ch) => ch.checked);
  checkboxes.forEach((c) => {
    c.checked = !state;
  });
});
