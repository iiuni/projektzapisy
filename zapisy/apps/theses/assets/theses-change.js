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

  const fieldsNames = {
    title: "Tytuł pracy",
    supporting_advisor: "Promotor wspierający",
    kind: "Typ",
    max_number_of_students: "Maksymalna liczba studentów",
    description: "Opis pracy dyplomowej",
  };

  const confirm_msg =
    "Zapisanie zmian spowoduje ponowne przesłanie pracy do komisji.\n" +
    "Czy na pewno chcesz zapisać zmiany w pracy dyplomowej?";

  document.querySelector(".confirm-submit").addEventListener(
    "submit",
    function () {
      let changedFields = [];

      for (const fieldName in importantFields) {
        if (importantFields[fieldName].value != old_instance[fieldName]) {
          changedFields.push(fieldsNames[fieldName]);
        }
      }

      if (changedFields.length > 1) {
        changed_field_list = "";
        changedFields.forEach((fieldName) => {
          changed_field_list += fieldName + ", ";
        });
        changed_field_list = changed_field_list.slice(0, -2);
        return confirm(
          `Zmieniono pola: ${changed_field_list}.\n${confirm_msg}`
        );
      }
      if (changedFields.length == 1) {
        return confirm(`Zmieniono pole: ${changedFields[0]}.\n${confirm_msg}`);
      }
    },
    false
  );
  document.getElementById("resetbtn").addEventListener(
    "click",
    function () {
      document.querySelector('[name="title"]').value = old_instance.title
      document.querySelector('[name="supporting_advisor"]').value = old_instance.supporting_advisor
      document.querySelector('[name="kind"]').value = old_instance.kind
      document.querySelector('[name="max_number_of_students"]').value = old_instance.max_number_of_students
      document.querySelector('textarea[name="description"]').value = old_instance.description
    },
    false
  );
};
