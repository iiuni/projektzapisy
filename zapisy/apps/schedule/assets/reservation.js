import "jquery";
const $ = jQuery;

var formsetCounter = 0;
var maxFormsetNumber = 0;

// Lista pozycji pustych formularzy terminów, które możemy
// dodać jako nowy termin. Jeśli na liście tej znajduje się
// liczba n, oznacza to, że idąc od góry n-ty formularz jest
// wolny. Liczby te są uporządkowane rosnąco.
var listOfEmpty = [];

/* Funkcja zmienia wygląd formularza w zależności od typu rezerwacji.
   Dla wydarzenia wyświetlamy pole tytułu i widoczności, dla egzaminu
   lub kolokwium dodatkowe pole wyboru przedmiotu. */
function setFormDisplay() {
  if ($("#form-type").val() == 2) {
    $("#form-course").addClass("d-none");
    $(".form-event").removeClass("d-none");
  } else {
    $("#form-course").removeClass("d-none");
    $(".form-event").addClass("d-none");
  }
}

/* Wyłącza edycję aktualnie aktywnych terminów. */
function setTermsToDefault() {
  $(".active-term").removeClass("active-term");
  $(".term-form")
    .find("input")
    .prop("disabled", true);
  $(".term-form")
    .find(".form-place")
    .removeClass("bg-light");
}

/* Włącza edycję danego terminu. */

function setEdited(object) {
  setTermsToDefault();
  $(object)
    .closest(".term-form")
    .addClass("active-term");
  $(object)
    .closest(".term-form")
    .find("input")
    .prop("disabled", false);
  $(object)
    .closest(".term-form")
    .find(".form-place")
    .addClass("bg-light");

  // Termin przestaje być oznaczony jako przeznaczony do usunięcia
  $(object)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", false);
}

function deleteTermClick(event) {
  event.preventDefault();

  $(event.target)
    .closest(".term-form")
    .addClass("d-none");

  $(event.target)
    .closest(".term-form")
    .find('input[name$="-DELETE"]')
    .prop("checked", true);

  // Jeżeli usuwamy termin który nie jest zapisany w bazie (ma niepuste id), to
  // formularz może być jeszcze w przyszłości użyty
  if (
    !$(event.target)
      .closest(".term-form")
      .find('input[name$="-id"]')
      .val()
  ) {
    formsetCounter -= 1;

    // Formularz jest umieszczony na końcu listy formularzy, aby przy ponownym
    // użyciu nie pojawił się pomiędzy istniejącymi formularzami.
    $(event.target)
      .closest(".term-form")
      .insertAfter($(".term-form").last());

    // Przesuwamy pozycję pustych formularzy o jeden do góry, ponieważ
    // usunięty formularz przesunęlismy na koniec
    for (let i = 0; i < listOfEmpty.length; i++) {
      listOfEmpty[i] -= 1;
    }

    // Dodajemy usunięty formularz na koniec listy
    listOfEmpty.push(maxFormsetNumber - 1);
  }
}

function newTermClick(event) {
  event.preventDefault();
  if (formsetCounter == maxFormsetNumber) return;

  if (!listOfEmpty) return;

  formsetCounter += 1;

  // Wybieramy pozycję pierwszego pustego formularza terminu
  // i usuwamy ją z listy pustych.
  var last = listOfEmpty.shift();

  // Znajdujemy wybrany element, wyświetlamy go i oznaczamy
  // jako aktualnie edytowany
  var newTermForm = $(".term-form").eq(last);
  newTermForm.removeClass("d-none");
  setEdited(newTermForm);
}

function editTermClick(event) {
  event.preventDefault();
  setEdited(event.target);
}

/* Odpowiada za ustawienie zewnętrznej lokacji. Lokacja 
   terminu zostaje ustawiona jako wartość pola zewnętrznej 
   lokacji, zaś pole wybranej sali zostaje wyczyszczone. */
function addOutsideLocation(event) {
  $(".active-term")
    .find(".form-room")
    .val("");
  $(".active-term")
    .find(".form-place")
    .val($("#inputplace").val());
}

function saveEvent(event) {
  event.preventDefault();
  $(".term-form")
    .find("input")
    .prop("disabled", false);
  $("#main-form").submit();
}

$(document).ready(() => {
  // Pobieramy otrzymaną z serwera liczbę formularzy.
  maxFormsetNumber = parseInt(
    $('input[name="term_set-TOTAL_FORMS"]').val()
  );

  // Otrzymujemy zawsze dodatkowo 10 formularzy terminów, które powinny
  // zostać ukryte. Pozostałe to albo jeden formularz podstawowy,
  // albo wcześniej dodane terminy.
  formsetCounter = maxFormsetNumber - 10;

  // Wyświetlamy formularze terminów, które nie przeszły walidacji.
  $(".term-form")
    .slice(formsetCounter, maxFormsetNumber)
    .each((id, el) => {
      if ($(el).find(".is-invalid")[0]) formsetCounter += 1;
    });

  // Dodajemy pozycje pustych formularzy terminów
  $(".term-form")
    .slice(0, formsetCounter)
    .removeClass("d-none");
  for (let i = formsetCounter; i < maxFormsetNumber; i++) {
    listOfEmpty.push(i);
  }

  setFormDisplay();
  $(document).on("change", "#form-type", setFormDisplay);

  $(document).on(
    "click",
    "#add-outside-location",
    addOutsideLocation
  );

  $(document).on("click", "#new-term-form", newTermClick);

  $(document).on(
    "click",
    ".delete-term-form",
    deleteTermClick
  );

  $(document).on("click", ".edit-term-form", editTermClick);

  $(document).on("click", "#save-event", saveEvent);
});
