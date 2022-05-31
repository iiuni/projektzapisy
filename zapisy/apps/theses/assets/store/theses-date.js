import dayjs from "dayjs";
import customParseFormat from "dayjs/plugin/customParseFormat";
import duration from "dayjs/plugin/duration";

dayjs.extend(customParseFormat);
dayjs.extend(duration);

function changeOfDateField(requiredDate, reservedUntil) {
  if (requiredDate) {
    reservedUntil.value = dayjs()
      .add(dayjs.duration({ years: 2 }))
      .format("YYYY-MM-DD");
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

if (!Boolean(reservedUntil.value) && !reservedUntil.disabled) {
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
