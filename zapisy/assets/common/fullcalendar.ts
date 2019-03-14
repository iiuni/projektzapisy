import * as $ from "jquery";
import "fullcalendar/dist/fullcalendar.css";
import "fullcalendar";

$(document).ready(() => {
   const data = JSON.parse($("#calendar-data")[0].innerHTML);
   for(const calendar of data){
      $(calendar.selector).fullCalendar(calendar.settings);
   }
});