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

// Fetches days from the url provided in classroom.html template.

async function fetchDaysFromEndpoint(endpoint, start, end) {
  const url = new URL(endpoint, window.location.origin);
  url.search = new URLSearchParams({
    start: start.toISOString(),
    end: end.toISOString(),
  });
  const response = await fetch(url);
  return response.json();
}

// Sets apropriate css classes for given dates

async function handleDaysFromEndpoint(dates, className, title, messageForDay) {
  if (dates.length !== 0) {
    const days = document.querySelectorAll(
      ".fc-daygrid-day, .fc-col-header-cell"
    );
    for (const day of days) {
      const index = dates.findIndex(
        (e) => e.day === day.getAttribute("data-date")
      );
      if (index > -1) {
        day.classList.add(className);
        day.setAttribute("title", title + messageForDay(index));
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", function () {
  const calendarEl = document.getElementById("calendar");

  const calendar = new Calendar(calendarEl, {
    plugins: [dayGridPlugin, timeGridPlugin, bootstrap5Plugin],

    datesSet: async function (dateInfo) {
      const changedDatesMapping = [
        "poniedziałkowe",
        "wtorkowe",
        "środowe",
        "czwartkowe",
        "piątkowe",
        "sobotnie",
        "niedzielne",
      ];
      const freeDates = await fetchDaysFromEndpoint(
        window.freedays,
        dateInfo.start,
        dateInfo.end
      );
      const changedDates = await fetchDaysFromEndpoint(
        window.changeddays,
        dateInfo.start,
        dateInfo.end
      );
      handleDaysFromEndpoint(
        freeDates,
        "free-day",
        "W tym dniu nie odbywają się zajęcia",
        (x) => ""
      );
      handleDaysFromEndpoint(
        changedDates,
        "change-day",
        "W tym dniu odbywają się zajęcia ",
        (x) => changedDatesMapping[changedDates[x].weekday - 1]
      );
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
