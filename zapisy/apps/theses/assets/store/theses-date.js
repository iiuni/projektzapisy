window.onload = function () {
  function changeOfDateField(requiredDate, reservedUntil) {
    if (requiredDate) {
      var reservedUntilDate = new Date();
      reservedUntilDate.setFullYear(reservedUntilDate.getFullYear() + 2);
      var dd = String(reservedUntilDate.getDate()).padStart(2, "0");
      var mm = String(reservedUntilDate.getMonth() + 1).padStart(2, "0");
      var yyyy = reservedUntilDate.getFullYear();
      reservedUntilDate = yyyy + "-" + mm + "-" + dd;

      reservedUntil.value = reservedUntilDate;
      reservedUntil.disabled = false;
      reservedUntil.required = true;
    } else {
      reservedUntil.value = "";
      reservedUntil.disabled = true;
      reservedUntil.required = false;
    }

    reservedUntil.classList.add("border-danger");
    var intervalID = setInterval(function () {
      if (reservedUntil.classList.contains("border-danger")) {
        reservedUntil.classList.remove("border-danger");
      }
    }, 1500);
  }

  var studentsSelect = document.getElementById("id_students");
  var reservedUntil = document.getElementById("id_reserved_until");

  var requiredDate = Boolean(
    studentsSelect.querySelectorAll("option:checked").length
  );

  if(!Boolean(reservedUntil.value) && !reservedUntil.disabled) {
    reservedUntil.disabled = true;
  }
  if (Boolean(reservedUntil.value) != requiredDate) {
    changeOfDateField(requiredDate, reservedUntil);
  }


  studentsSelect.addEventListener("change", function handleChange(event) {
    if (
      Boolean(studentsSelect.querySelectorAll("option:checked").length) !=
      requiredDate
    ) {
      requiredDate = !requiredDate;
      changeOfDateField(requiredDate, reservedUntil);
    } else if (Boolean(reservedUntil.value) != requiredDate) {
      changeOfDateField(requiredDate, reservedUntil);
    }
  });
};
