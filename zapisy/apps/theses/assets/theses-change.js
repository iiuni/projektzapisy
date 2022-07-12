window.onload = function () {
  const old_instance = JSON.parse(
    document.getElementById("old_instance").textContent
  );

  $(document).on("submit", ".confirm-submit", function () {
    const confirm_msg =
      "Zapisanie zmian spowoduje ponowne przesłanie pracy do komisji.\n" +
      "Czy na pewno chcesz zapisać zmiany w pracy dyplomowej?";
    if (document.querySelector('[name="title"]').value != old_instance.title) {
      return confirm(`Zmieniono tytuł pracy.\n${confirm_msg}`);
    }
    if (
      document.querySelector('[name="supporting_advisor"]').value !=
      old_instance.supporting_advisor
    ) {
      return confirm(`Zmieniono promotora wspierającego.\n${confirm_msg}`);
    }
    if (document.querySelector('[name="kind"]').value != old_instance.kind) {
      return confirm(`Zmieniono typ pracy.\n${confirm_msg}`);
    }
    if (
      document.querySelector('[name="max_number_of_students"]').value !=
      old_instance.max_number_of_students
    ) {
      return confirm(`Zmieniono maks. liczba studentów.\n${confirm_msg}`);
    }
    if (
      document.querySelector('textarea[name="description"]').value !=
      old_instance.description
    ) {
      return confirm(`Zmieniono opis pracy.\n${confirm_msg}`);
    }
  });
};
