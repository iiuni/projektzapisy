window.onload = function () {
  // Object old_instance contains the accepted, but mutable parameters of the thesis:
  // title, supporting_avisor, kind, max_number_of_students and description.
  const old_instance = JSON.parse(
    document.getElementById("old_instance").textContent
  );

  // Changing any of the accepted parameters
  // switches the thesis back to the BEING_EVALUATED state
  document
    .getElementById("confirm-submit")
    .addEventListener("submit", function (evt) {
      let changedFields = Object.keys(old_instance)
        .filter(function (fieldName) {
          return (
            document.querySelector(`#confirm-submit [name=${fieldName}]`)
              .value != old_instance[fieldName]
          );
        })
        .map(function (fieldName) {
          return document
            .querySelector(`[for=id_${fieldName}]`)
            .childNodes[0].nodeValue.trim();
        });

      changed_field_str = changedFields.join(", ");

      if (changedFields.length > 0) {
        let msg =
          `Zmieniono ${
            changedFields.length == 1 ? "pole" : "pola"
          }: ${changed_field_str}.\n` +
          `Zapisanie zmian spowoduje ponowne przesłanie pracy do komisji. ` +
          `Czy na pewno chcesz zapisać zmiany w pracy dyplomowej?`;

        return confirm(msg) || evt.preventDefault();
      }
    });

  // The reset button allows the user to reset changes
  // made to accepted parameters.
  document.getElementById("resetbtn").addEventListener(
    "click",
    function () {
      for (const fieldName in old_instance) {
        document.querySelector(`#confirm-submit [name=${fieldName}]`).value =
          old_instance[fieldName];
      }
    },
    false
  );
};
