window.onload = function () {
  const old_instance = JSON.parse(
    document.getElementById("old_instance").textContent
  );

  document
    .querySelector(".confirm-submit")
    .addEventListener("submit", function (evt) {
      let changedFields = Object.keys(old_instance)
        .filter(function (fieldName) {
          return (
            document.querySelector(`.confirm-submit [name=${fieldName}]`)
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

  document.getElementById("resetbtn").addEventListener(
    "click",
    function () {
      const Fields = Object.keys(old_instance);
      for (const fieldName in Fields) {
        if (Fields[fieldName] == "description") {
          document.querySelector(`textarea[name=${Fields[fieldName]}]`).value =
            old_instance[Fields[fieldName]];
        } else {
          document.querySelector(`[name=${Fields[fieldName]}]`).value =
            old_instance[Fields[fieldName]];
        }
      }
    },
    false
  );
};
