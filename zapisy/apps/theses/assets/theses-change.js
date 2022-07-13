window.onload = function () {
  const old_instance = JSON.parse(
    document.getElementById("old_instance").textContent
  );

  const importantFields = {
    title: document.querySelector('[name="title"]'),
    supporting_advisor: document.querySelector('[name="supporting_advisor"]'),
    kind: document.querySelector('[name="kind"]'),
    max_number_of_students: document.querySelector(
      '[name="max_number_of_students"]'
    ),
    supporting_advisor: document.querySelector('[name="supporting_advisor"]'),
    description: document.querySelector('textarea[name="description"]'),
  };

  document
    .querySelector(".confirm-submit")
    .addEventListener("submit", function (evt) {
      let changedFields = Object.keys(importantFields)
        .filter(function (fieldName) {
          return importantFields[fieldName].value != old_instance[fieldName];
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
      for (const fieldName in importantFields) {
        importantFields[fieldName].value = old_instance[fieldName];
      }
    },
    false
  );
};
