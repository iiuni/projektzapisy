import { debounce } from "lodash";

// Django's <select>
const djangoField = document.getElementById("id_students");
// Its layout column
const djangoFieldColumn = djangoField.parentElement.parentElement.parentElement;
// New layout column to place next to the django one
const searchFieldColumn = document.createElement("div");
searchFieldColumn.className = djangoFieldColumn.className;
const studentSearchInput = document.createElement("input");
studentSearchInput.type = "search";
studentSearchInput.autocomplete = "off";
studentSearchInput.className = "form-control";
studentSearchInput.placeholder =
  "Szukaj po imieniu, nazwisku, numerze indeksu\u2026";
studentSearchInput.id = "student-search-input";
studentSearchInput.addEventListener(
  "input",
  debounce(updateSearchResults, 300)
);

const studentSearchInputLabel = document.createElement("label");
studentSearchInputLabel.textContent = "Wyszukiwarka studentów";
studentSearchInputLabel.htmlFor = "student-search-input";

const studentSearchResultList = document.createElement("div");
studentSearchResultList.className = "list-group list-group-flush";
studentSearchResultList.style.position = "absolute";
studentSearchResultList.style.top = "calc(100% + 0.5rem)";
studentSearchResultList.style.border =
  "1px solid var(--bs-list-group-border-color)";
studentSearchResultList.style.borderRadius =
  "var(--bs-list-group-border-radius)";
studentSearchResultList.style.width = "100%";
studentSearchResultList.style.maxHeight = "15rem";
studentSearchResultList.style.overflow = "auto";
// A snippet to include a sibling selector without a .css file
// Hides the result list if it's empty (the border is still visible otherwise)
const style = document.createElement("style");
style.innerHTML = `
#student-search-input + div:not(:has(> *)) {
  display: none;
}
`;
document.body.append(style);

const studentSearchContainer = document.createElement("div");
studentSearchContainer.style.position = "relative";
studentSearchContainer.append(studentSearchInput);
studentSearchContainer.append(studentSearchResultList);
searchFieldColumn.append(studentSearchInputLabel);
searchFieldColumn.append(studentSearchContainer);
djangoFieldColumn.before(searchFieldColumn);

/**
 * Fetch students matching the query, or clear the result list for an empty query
 * and update the list on the left, based on the internal list
 */
async function updateSearchResults() {
  const search = studentSearchInput.value;
  if (search.length === 0) {
    clearSearchResultList();
    return;
  }

  const { students: fetchedStudents } = await fetchStudents(search);

  const notAssignedStudents = fetchedStudents.filter((fetchedStudent) =>
    assignedStudents.every((s) => s.value !== fetchedStudent.value)
  );

  // Replace the content with new one
  studentSearchResultList.replaceChildren(
    ...notAssignedStudents.map(createStudentSearchResultListItem)
  );
}

/**
 * Update the list on the right, based on the internal list
 */
function updateAssignedStudentsList() {
  if (assignedStudents.length === 0) {
    assignedStudentsList.innerHTML = "Brak przypisanych studentów.";
    return;
  }

  assignedStudentsList.innerHTML = "";
  assignedStudentsList.append(
    ...assignedStudents.map(createAssignedStudentListItem)
  );
}

/**
 * Update the hidden django <select>, based on the internal list
 */
function updateDjangoField() {
  djangoField.innerHTML = "";
  djangoField.append(...assignedStudents.map(createSelectOption));
}

/**
 * Create an item for the hidden django <select>
 */
function createSelectOption(student) {
  const option = document.createElement("option");
  option.value = student.value.toString();
  option.text = student.label;
  option.selected = true;
  return option;
}

function assignStudent(student) {
  if (assignedStudents.includes(student)) {
    return;
  }

  assignedStudents.push(student);
  updateAssignedStudentsList();
  updateDjangoField();
  updateSearchResults();
}

function unassignStudent(student) {
  if (!assignedStudents.includes(student)) {
    return;
  }

  assignedStudents.splice(
    assignedStudents.findIndex((s) => s.value === student.value),
    1
  );
  updateAssignedStudentsList();
  updateDjangoField();
  updateSearchResults();
}

async function fetchStudents(substring) {
  const ajaxUrlInput = document.querySelector("input#ajax-url");

  if (ajaxUrlInput === null) {
    throw new Error("#ajax-url not found.");
  }

  const ajaxUrl = ajaxUrlInput.value;
  const urlSafeSubstring = encodeURIComponent(substring);
  const response = await fetch(`${ajaxUrl}/${urlSafeSubstring}`);
  return response.json();
}

function clearSearchResultList() {
  studentSearchResultList.textContent = "";
}

/**
 * Create an item for the list on the left
 */
function createStudentSearchResultListItem(student) {
  const listItem = document.createElement("div");
  listItem.textContent = student.label;
  listItem.className =
    "list-group-item d-flex align-items-center justify-content-between";

  const assignStudentButton = document.createElement("button");
  assignStudentButton.textContent = "Przypisz";
  assignStudentButton.className = "btn btn-success";
  assignStudentButton.addEventListener("click", (ev) => {
    ev.preventDefault();
    assignStudent(student);
  });
  listItem.append(assignStudentButton);

  return listItem;
}

/**
 * Create an item for the list on the right
 */
function createAssignedStudentListItem(student) {
  const listItem = document.createElement("div");
  listItem.textContent = student.label;
  listItem.className =
    "list-group-item d-flex align-items-center justify-content-between";

  const unassignStudentButton = document.createElement("button");
  unassignStudentButton.textContent = "Usuń";
  unassignStudentButton.className = "btn btn-danger";
  unassignStudentButton.addEventListener("click", (ev) => {
    ev.preventDefault();
    unassignStudent(student);
  });
  listItem.append(unassignStudentButton);

  return listItem;
}

// Handle students that are already assigned (when editing a thesis)
const assignedStudents = Array.from(djangoField.options).map((option) => ({
  value: Number(option.value),
  label: option.text,
}));

const assignedStudentsList = document.createElement("div");
assignedStudentsList.className = "list-group";
djangoField.before(assignedStudentsList);
updateAssignedStudentsList();

// Hide the django <select>
djangoField.style.display = "none";
