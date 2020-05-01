import "jquery";
const $ = jQuery;

function setEdited(object) {
  $(".active-term").removeClass("active-term");
  $(object).closest("form").addClass("active-term");
  $("#term-formset").find("input").prop("disabled", true);
  $("#term-formset")
    .find(".form-place")
    .removeClass("bg-light");
  $(object)
    .closest("form")
    .find("input")
    .prop("disabled", false);
  $(object)
    .closest("form")
    .find(".form-place")
    .addClass("bg-light");
}
function deleteTermClick(event) {
  event.preventDefault();
  $(event.target).closest("form").remove();
}

function editTermClick(event) {
  event.preventDefault();
  setEdited(event.target);
}

$(document).ready(() => {
  $("#addoutsidelocation").click((event) => {
    console.log($("#inputplace").val());
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
    $("#main-form").submit();
  });

  $("#new-term-form").click((event) => {
    var cloned = $("form").last().clone();
    cloned.insertBefore($("#new-term-form"));
    cloned.find(".row").find("input").val("").end();
    setEdited(cloned.find(".edit-term-form"));
  });
});
