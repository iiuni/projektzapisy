import "jquery";
const $ = jQuery;

var formsetCounter = 0;
var maxFormsetNumber = 0;
var listOfEmpty = [];

function setFormDisplay() {
  if ($("#form-type").val() == 2) {
    $("#form-course").addClass("d-none");
    $(".form-event").removeClass("d-none");
  } else {
    $("#form-course").removeClass("d-none");
    $(".form-event").addClass("d-none");
  }
}

function setTermsToDefault() {
  $(".active-term").removeClass("active-term");
  $(".term-form")
    .find("input")
    .prop("disabled", true);
  $(".term-form")
    .find(".form-place")
    .removeClass("bg-light");
}

function setEdited(object) {
  setTermsToDefault();
  $(object)
    .closest(".term-form")
    .addClass("active-term");
  $(object)
    .closest(".term-form")
    .find("input")
    .prop("disabled", false);
  $(object)
    .closest(".term-form")
    .find(".form-place")
    .addClass("bg-light");

  $(object)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", false);
}

function deleteTermClick(event) {
  event.preventDefault();

  $(event.target)
    .closest(".term-form")
    .addClass("d-none");

  $(event.target)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", true);

  if (
    !$(event.target)
      .closest(".term-form")
      .find('input[name$="-id"]')
      .val()
  ) {
    formsetCounter -= 1;
    $(event.target)
      .closest(".term-form")
      .insertAfter($(".term-form").last());
    for (let i = 0; i < listOfEmpty.length; i++) {
      listOfEmpty[i] -= 1;
    }
    listOfEmpty.push(maxFormsetNumber - 1);
  }
}

function newTermClick(event) {
  event.preventDefault();
  if (formsetCounter == maxFormsetNumber) return;

  if (!listOfEmpty) return;

  formsetCounter += 1;

  var last = listOfEmpty.shift();

  var newTermForm = $(".term-form").eq(last);
  newTermForm.removeClass("d-none");
  setEdited(newTermForm);
}

function editTermClick(event) {
  event.preventDefault();
  setEdited(event.target);
}

function addOutsideLocation(event) {
  $(".active-term")
    .find(".form-room")
    .val("");
  $(".active-term")
    .find(".form-place")
    .val($("#inputplace").val());
}

function saveEvent(event) {
  event.preventDefault();
  $(".term-form")
    .find("input")
    .prop("disabled", false);
  $("#main-form").submit();
}

$(document).ready(() => {
  maxFormsetNumber = parseInt(
    $('input[name="term_set-TOTAL_FORMS"]').val()
  );

  formsetCounter = maxFormsetNumber - 3;
  $(".term-form")
    .slice(0, formsetCounter)
    .removeClass("d-none");
  for (let i = formsetCounter; i < maxFormsetNumber; i++) {
    listOfEmpty.push(i);
  }

  setFormDisplay();
  $(document).on("change", "#form-type", setFormDisplay);

  $(document).on(
    "click",
    "#add-outside-location",
    addOutsideLocation
  );

  $(document).on("click", "#new-term-form", newTermClick);

  $(document).on(
    "click",
    ".delete-term-form",
    deleteTermClick
  );

  $(document).on("click", ".edit-term-form", editTermClick);

  $(document).on("click", "#save-event", saveEvent);
});
