// Implements asynchronous semester fetching.
//
// This script is meant to be used with semester_dropdown.html dropdown menu.
// Installs two event listeners to asynchronously fetch data of semesters
// chosen from dropdown menu. Elements to be changed must contain attribute
// data-js-sem-depend and an id. Updating Vue components is implemented
// via dispatching custom event "timetable-change".

const timetableChangeEvent = new CustomEvent("timetable-change");
async function fetch_new_semester(url: string) {
  const response = await fetch(url);
  if (!response.ok) {
    return;
  }
  const dataJSON = await response.text();
  const dataObj = JSON.parse(dataJSON);
  let semesterDependentElements = document.querySelectorAll(
    "[data-js-sem-depend]"
  );
  for (let elem of semesterDependentElements) {
    if (!elem.id) {
      continue;
    }
    let elemData = dataObj[elem.id];
    let elemContainer = document.getElementById(elem.id);
    if (elemData && elemContainer) {
      elemContainer.innerHTML = elemData;
    }
  }
}
let semesterDropdown = document.getElementById("semester-dropdown-menu");
if (semesterDropdown !== null) {
  semesterDropdown.addEventListener(
    "click",
    async (event) => {
      const target = event.target;
      if (target instanceof HTMLElement && target.closest("[data-js-link]")) {
        let capturedUrl = target.getAttribute("href");
        if (capturedUrl !== null) {
          event.preventDefault();
          capturedUrl = capturedUrl.trim();
          if (capturedUrl === window.location.pathname) {
            return;
          }
          const targetUrl = capturedUrl + "fetch/";
          await fetch_new_semester(targetUrl);
          window.dispatchEvent(timetableChangeEvent);
          history.pushState({}, "", capturedUrl);
        }
      }
    },
    true
  );
  window.addEventListener("popstate", async (event) => {
    event.preventDefault();
    let destUrl = window.location.pathname + "fetch/";
    await fetch_new_semester(destUrl);
    window.dispatchEvent(timetableChangeEvent);
  });
}
