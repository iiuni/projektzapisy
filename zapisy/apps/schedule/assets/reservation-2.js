import "jquery";
const $ = jQuery;

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
}

function cloneTermForm() {
  var cloned = $(".term-form").last().clone();
  cloned = cloned.insertBefore($("#new-term-form"));

  var counter = parseInt(
    $('input[name="term_set-TOTAL_FORMS"]').val()
  );
  let namePrefix = "term_set-" + counter + "-";
  $('input[name="term_set-TOTAL_FORMS"]').val(
    parseInt(counter) + 1
  );

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

  cloned.find(".row").find("input").val("").end();
}

function deleteTermClick(event) {
  event.preventDefault();
  var counter = parseInt(
    $('input[name="term_set-TOTAL_FORMS"]').val()
  );

  if (counter != 1) {
    $('input[name="term_set-TOTAL_FORMS"]').val(
      parseInt(counter) - 1
    );
    $(event.target).closest(".term-form").remove();
  }
}

function editTermClick(event) {
  event.preventDefault();
  setEdited(event.target);
}

$(document).ready(() => {
  $("#addoutsidelocation").click((event) => {
    $(".active-term").find(".form-room").val("");
    $(".active-term")
      .find(".form-place")
      .val($("#inputplace").val());
  });

  //On reservation type = event, display title field. Otherwise hide it.
  $("#form-type").change(function (event) {
    if ($("#form-type").val() == 2) {
      $("#form-course").addClass("d-none");
      $(".form-event").removeClass("d-none");
    } else {
      $("#form-course").removeClass("d-none");
      $(".form-event").addClass("d-none");
    }
  });

  $(document).on(
    "click",
    ".delete-term-form",
    deleteTermClick
  );

  $(document).on("click", ".edit-term-form", editTermClick);

  $(document).on("click", "#save-event", (event) => {
    event.preventDefault();
    $(".term-form").find("input").prop("disabled", false);
    $("#main-form").submit();
  });

  $("#new-term-form").click((event) => {
    event.preventDefault();
    cloneTermForm();
    setEdited(
      $(".term-form").last().find(".edit-term-form")
    );
  });
});
