import { Calendar } from '@fullcalendar/core';

document.addEventListener('DOMContentLoaded', function() {
  const calendarEl = document.getElementById('calendar');

  var calendar = new Calendar(calendarEl, {
  });

  calendar.render();
});
