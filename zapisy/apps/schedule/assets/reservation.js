import "jquery";
const $ = jQuery;

var formsetCounter = 0;

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
  $(".term-form").find("input").prop("disabled", true);
  $(".term-form")
    .find(".form-place")
    .removeClass("bg-light");
}

function setEdited(object) {
  setTermsToDefault();
  $(object).closest(".term-form").addClass("active-term");
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

function cloneTermForm() {
  let cloned = $(".term-form").last().clone();
  cloned = cloned.insertBefore($("#new-term-form"));

  let counter = parseInt(
    $('input[name="term_set-TOTAL_FORMS"]').val()
  );
  $('input[name="term_set-TOTAL_FORMS"]').val(
    parseInt(counter) + 1
  );
  formsetCounter += 1;

  let namePrefix = "term_set-" + counter + "-";

  cloned.find(".form-day").attr("name", namePrefix + "day");
  cloned
    .find(".form-start")
    .attr("name", namePrefix + "start");
  cloned.find(".form-end").attr("name", namePrefix + "end");
  cloned
    .find(".form-place")
    .attr("name", namePrefix + "place");
  cloned
    .find(".form-room")
    .attr("name", namePrefix + "room");
  cloned
    .find('input[name$="-DELETE"]')
    .attr("name", namePrefix + "DELETE");

  cloned.find(".row").find("input").val("").end();
  cloned.removeClass("d-none");
  cloned
    .find('input[name$="-DELETE"]')
    .prop("checked", true);
}

function deleteTermClick(event) {
  event.preventDefault();

  formsetCounter =
    formsetCounter == 0 ? 0 : formsetCounter - 1;

  $(event.target).closest(".term-form").addClass("d-none");

  $(event.target)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", true);
}

function newTermClick(event) {
  event.preventDefault();
  cloneTermForm();
  setEdited($(".term-form").last().find(".edit-term-form"));
}

function editTermClick(event) {
  event.preventDefault();
  setEdited(event.target);
}

function addOutsideLocation(event) {
  $(".active-term").find(".form-room").val("");
  $(".active-term")
    .find(".form-place")
    .val($("#inputplace").val());
}

function saveEvent(event) {
  event.preventDefault();
  $(".term-form").find("input").prop("disabled", false);
  $("#main-form").submit();
}

$(document).ready(() => {
  formsetCounter = parseInt(
    $('input[name="term_set-TOTAL_FORMS"]').val()
  );

  //On reservation type = event, display title field. Otherwise hide it.
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
