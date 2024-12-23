import { debounce } from "lodash";

const djangoField = document.getElementById("id_students");
const djangoFieldColumn = djangoField.parentElement.parentElement.parentElement;
const searchFieldColumn = document.createElement("div");
searchFieldColumn.className = djangoFieldColumn.className;
const studentSearchInput = document.createElement("input");
studentSearchInput.type = "search";
studentSearchInput.autocomplete = "off";
studentSearchInput.className = "form-control";
studentSearchInput.placeholder = "Szukaj po imieniu, nazwisku, numerze indeksu\u2026";
studentSearchInput.id = "student-search-input";
studentSearchInput.addEventListener("input", debounce(function (ev) {
  updateSearchResults(this.value);
}, 300));

const studentSearchInputLabel = document.createElement("label");
studentSearchInputLabel.textContent = "Wyszukiwarka studentów";
studentSearchInputLabel.htmlFor = "student-search-input";

const studentSearchResultList = document.createElement("div");
studentSearchResultList.className = "list-group list-group-flush";
studentSearchResultList.style.position = "absolute";
studentSearchResultList.style.top = "calc(100% + 0.5rem)";
studentSearchResultList.style.border = "1px solid var(--bs-list-group-border-color)";
studentSearchResultList.style.borderRadius = "var(--bs-list-group-border-radius)";
studentSearchResultList.style.width = "100%";
studentSearchResultList.style.maxHeight = "15rem";
studentSearchResultList.style.overflow = "auto";
const style = document.createElement('style');
style.innerHTML =
`
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

async function updateSearchResults(search) {
  if (search.length === 0) {
    clearSearchResults();
    return;
  }
  
  const { students: fetchedStudents } = await fetchStudents(search);
  
  const notAssignedStudents = fetchedStudents.filter((fetchedStudent) =>
    assignedStudents.every((s) => s.value !== fetchedStudent.value)
  );

  searchResults.splice(0, searchResults.length, ...notAssignedStudents);
  studentSearchResultList.replaceChildren(...searchResults.map(createStudentSearchResultListItem));
}

function updateAssignedStudentsList() {
  if (assignedStudents.length === 0) {
    assignedStudentsList.innerHTML = "Brak przypisanych studentów.";
    return;
  }

  assignedStudentsList.innerHTML = "";
  assignedStudentsList.append(...assignedStudents.map(createAssignedStudentListItem));
}

function updateDjangoField() {
  djangoField.innerHTML = "";
  djangoField.append(...assignedStudents.map(createSelectOption));
}

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
  updateSearchResults(studentSearchInput.value);
}

function unassignStudent(student) {
  if (!assignedStudents.includes(student)) {
    return;
  }
    
  assignedStudents.splice(assignedStudents.findIndex((s) => s.value === student.value), 1);
  updateAssignedStudentsList();
  updateDjangoField();
  updateSearchResults(studentSearchInput.value);
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
};

const searchResults = [];

function clearSearchResults() {
  searchResults.splice(0);
  studentSearchResultList.textContent = "";
}

function createStudentSearchResultListItem(student) {
  const listItem = document.createElement("div");
  listItem.textContent = student.label;
  listItem.className = "list-group-item d-flex align-items-center justify-content-between";

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

function createAssignedStudentListItem(student) {
  const listItem = document.createElement("div");
  listItem.textContent = student.label;
  listItem.className = "list-group-item d-flex align-items-center justify-content-between";
  
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

const assignedStudents = Array.from(djangoField.options).map((option) => ({
  value: Number(option.value),
  label: option.text,
}));

const assignedStudentsList = document.createElement("div");
assignedStudentsList.className = "list-group";
djangoField.before(assignedStudentsList);
updateAssignedStudentsList();

djangoField.style.display = "none";
