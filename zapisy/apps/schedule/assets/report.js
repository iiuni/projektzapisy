document.addEventListener("DOMContentLoaded", () => {
  // zaznacz wszystkie sale do raportu
  document.querySelectorAll(".select-all-button").forEach((e) => {
    const grandpa = e.parentElement.parentElement;
    const select = grandpa.querySelector("select[name=rooms]");
    if (select === undefined) {
      return;
    }
    e.onclick = (event) => {
      for (const opt of select.options) {
        opt.selected = true;
      }
    };
  });

  // Print button.
  const printButton = document.getElementById("print-report");
  if (printButton) {
    printButton.addEventListener("click", () => {
      window.print();
    });
  }

  const roomSelects = document.querySelectorAll("select[name=rooms]");
  roomSelects.forEach((el) => {
    el.classList.add("form-control");
  });

  document.getElementById("id_week").classList.add("form-control");
});
