import { Calendar } from "@fullcalendar/core";
import plLocale from "@fullcalendar/core/locales/pl";
import bootstrap5Plugin from "@fullcalendar/bootstrap5";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";

// Fetches events from the url provided in classroom.html template.

async function fetchEvents(fetchInfo) {
  const url = new URL(window.eventsURL, window.location.origin);
  url.search = new URLSearchParams({
    start: fetchInfo.start.toISOString(),
    end: fetchInfo.end.toISOString(),
  });
  const response = await fetch(url);
  return response.json();
}

// Fetches freedays from the url provided in classroom.html template.

async function fetchFreedays(start, end) {
  const url = new URL(window.freedays, window.location.origin);
  url.search = new URLSearchParams({
    start: start.toISOString(),
    end: end.toISOString(),
  });
  const response = await fetch(url);
  return response.json();
}

// Fetches changed days from the url provided in classroom.html template.

async function fetchChangedays(start, end) {
  const url = new URL(window.changedays, window.location.origin);
  url.search = new URLSearchParams({
    start: start.toISOString(),
    end: end.toISOString(),
  });
  const response = await fetch(url);
  return response.json();
}

// Sets apropriate css classes for freedays

async function handleFreedays(start, end) {
  const freeDates = await fetchFreedays(start, end);
  if (freeDates.length !== 0) {
    const days = document.querySelectorAll(
      ".fc-daygrid-day, .fc-col-header-cell"
    );
    for (const day of days) {
      const index = freeDates.findIndex(
        (e) => e.day === day.getAttribute("data-date")
      );
      if (index > -1) {
        day.classList.add("free-day");
        day.setAttribute("title", "W tym dniu nie odbywają się zajęcia");
      }
    }
  }
}

// Sets apropriate css classes for changed days

async function handleChangedays(start, end) {
  const changeDatesMapping = [
    "poniedziałkowe",
    "wtorkowe",
    "środowe",
    "czwartkowe",
    "piątkowe",
    "sobotnie",
    "niedzielne",
  ];
  const changeDates = await fetchChangedays(start, end);
  if (changeDates.length !== 0) {
    const days = document.querySelectorAll(
      ".fc-col-header-cell, .fc-daygrid-day"
    );
    for (const day of days) {
      const index = changeDates.findIndex(
        (e) => e.day === day.getAttribute("data-date")
      );
      if (index > -1) {
        day.classList.add("change-day");
        day.setAttribute(
          "title",
          "W tym dniu odbywają się " +
            changeDatesMapping[changeDates[index].weekday - 1] +
            " zajęcia"
        );
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");

  const calendar = new Calendar(calendarEl, {
    plugins: [dayGridPlugin, timeGridPlugin, bootstrap5Plugin],

    datesSet: async function (dateInfo) {
      handleFreedays(dateInfo.start, dateInfo.end);
      handleChangedays(dateInfo.start, dateInfo.end);
    },

    themeSystem: "bootstrap5",
    initialView: "timeGridWeek",
    locale: plLocale,

    buttonText: {
      prev: "<",
      next: ">",
    },
    height: "auto",

    allDaySlot: false,
    slotMinTime: "08:00:00",
    slotMaxTime: "22:00:00",

    headerToolbar: {
      start: "prev,next today",
      center: "title",
      end: "timeGridDay,timeGridWeek,dayGridMonth",
    },

    events: fetchEvents,
  });

  calendar.render();
});
