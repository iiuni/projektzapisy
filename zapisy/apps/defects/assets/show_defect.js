import "jquery";
const $ = jQuery;

function showForm(event) {
  event.preventDefault();
  $("#info-div").addClass("d-none");
  $("#info-form-div").removeClass("d-none");
}

$(function () {
  $(".pop").on("click", function () {
    $(".imagepreview").attr("src", $(this).find("img").attr("src"));
    $("#imagemodal").modal("show");
  });

  $("#show-info-form-button").on("click", showForm);
});
