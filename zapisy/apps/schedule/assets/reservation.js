// The following code is responsible for display of reservation form
// and management of terms formset, including adding, removing and
// editing reservation terms.

import "jquery";
const $ = jQuery;

let formsetCounter = 0;
let maxFormsetNumber = 0;
let extraTermsNumber = 0;

// List of positions of empty term forms that are available
// to add to the formset as new term forms. If list contains
// number n, it means, that the nth form from the top is
// available. List is in ascending order.
const listOfEmpty = [];

// Changes display of the form regarding to chosen reservation
// type. For event it displays title and visibility fields.
// For exams it displays course choice field.
function setFormDisplay() {
  if ($("#form-type").val() === "2") {
    $("#form-course").addClass("d-none");
    $(".form-event").removeClass("d-none");
  } else {
    $("#form-course").removeClass("d-none");
    $(".form-event").addClass("d-none");
  }
}

// Disables edition of currently active terms.
function setTermsToDefault() {
  $(".active-term").removeClass("active-term");
  $(".term-form").find("input").prop("disabled", true);
  $(".term-form").find(".form-place").removeClass("bg-light");
}

// Enables edition of given term.
function setEdited(object) {
  setTermsToDefault();
  $(object).closest(".term-form").addClass("active-term");
  $(object).closest(".term-form").find("input").prop("disabled", false);
  $(object).closest(".term-form").find(".form-place").addClass("bg-light");

  // Unmarks term as planned to be deleted.
  $(object)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", false);
}

// Deletes term
function deleteTermClick(event) {
  event.preventDefault();

  $(event.target).closest(".term-form").addClass("d-none");

  $(event.target)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", true);

  // If the term is not in the database (has empty id value), then the form
  // can be reused, so we append it to the listOfEmpty.
  if (!$(event.target).closest(".term-form").find('input[name$="-id"]').val()) {
    formsetCounter -= 1;

    // Form is moved to the end of the list of forms to make sure it will
    // not appear between existing forms when reused.
    $(event.target).closest(".term-form").insertAfter($(".term-form").last());

    // As we moved our form to the end of the list, we need to extend
    // listOfEmpty. As in list we keep only positions of empty forms, we
    // only have to append new position to the beginning of the list.
    const newPos =
      listOfEmpty.length != 0 ? listOfEmpty[0] - 1 : maxFormsetNumber - 1;
    listOfEmpty.unshift(newPos);
  }
}

function newTermClick(event) {
  event.preventDefault();
  if (formsetCounter === maxFormsetNumber) return;

  if (!listOfEmpty) return;

  formsetCounter += 1;

  // We choose position of the first empty term form and remove it from
  // listOfEmpty.
  const first = listOfEmpty.shift();

  // We find chosen element, display it and mark as active.
  const newTermForm = $(".term-form").eq(first);
  newTermForm.removeClass("d-none");
  setEdited(newTermForm);
}

function editTermClick(event) {
  event.preventDefault();
  setEdited(event.target);
}

// Handles setting outside location. The place field is
// set as outside location field value, and room field is cleaned.
function addOutsideLocation(event) {
  $(".active-term").find(".form-room").val("");
  $(".active-term").find(".form-place").val($("#inputplace").val());
}

function saveEvent(event) {
  event.preventDefault();
  $(".term-form").find("input").prop("disabled", false);
  $("#main-form").submit();
}

$(document).ready(() => {
  // We get number of term forms received from server.
  maxFormsetNumber = parseInt($('input[name="term_set-TOTAL_FORMS"]').val());

  // We get number of extra term forms (empty ones) received from server
  extraTermsNumber = parseInt($("#extra-terms-number").val());

  // Extra terms in formset should remain hidden, as they are empty.
  // The rest is either one basic term form or terms that are already in
  // database, so they should be displayed.
  formsetCounter = maxFormsetNumber - extraTermsNumber;

  // Displaying term forms that are invalid.
  $(".term-form")
    .slice(formsetCounter, maxFormsetNumber)
    .each((id, el) => {
      if ($(el).find(".is-invalid")[0]) formsetCounter += 1;
    });

  // We add position of available term forms to listOfEmpty.
  $(".term-form").slice(0, formsetCounter).removeClass("d-none");
  for (let i = formsetCounter; i < maxFormsetNumber; i++) {
    listOfEmpty.push(i);
  }

  setFormDisplay();
  $(document).on("change", "#form-type", setFormDisplay);

  $(document).on("click", "#add-outside-location", addOutsideLocation);

  $(document).on("click", "#new-term-form", newTermClick);

  $(document).on("click", ".delete-term-form", deleteTermClick);

  $(document).on("click", ".edit-term-form", editTermClick);

  $(document).on("click", "#save-event", saveEvent);
});
