<template>
  <div>
    <Filters @refetchEvents="refetchEvents" ref="filtersComponent" />
    <Reservation
      @refetchEvents="refetchEvents"
      @addEvent="addEvent"
      @unselect="unselect"
      @hideEventById="hideEventById"
      ref="reservationComponent"
    />
    <FullCalendar :options="calendarOptions" ref="calendarComponent" />
  </div>
</template>

<script>
import axios from "axios";
import FullCalendar from "@fullcalendar/vue";
import plLocale from "@fullcalendar/core/locales/pl";
import bootstrapPlugin from "@fullcalendar/bootstrap";
import interactionPlugin from "@fullcalendar/interaction";
import dayGridPlugin from "@fullcalendar/daygrid";
import timeGridPlugin from "@fullcalendar/timegrid";
import Reservation from "./Reservation.vue";
import Filters from "./Filters.vue";

// Sets header for all POST requests to enable CSRF protection.
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

// Rejected events of all types are transparent, so we need to convert
// hex to rgba, as hex colors do not work with alpha.
const convertHexToRGBA = (hex, opacity) => {
    let tempHex = hex.replace('#', '')
    if (tempHex.length === 3) {
        tempHex += tempHex
    }
    const r = parseInt(tempHex.substring(0, 2), 16)
    const g = parseInt(tempHex.substring(2, 4), 16)
    const b = parseInt(tempHex.substring(4, 6), 16)

    return `rgba(${r},${g},${b},${opacity / 100})`
}

const event_type_map = {
  0: "#dc3545", // exam
  1: "#fd7e14", // test
  2: "#007bff", // event
  3: "#28a745", // class
  5: "#6f42c1", // special_reservation
};

export default {
  components: {
    FullCalendar, // make the <FullCalendar> tag available
    Reservation,
    Filters,
  },
  data() {
    return {
      calendarOptions: {
        plugins: [
          interactionPlugin,
          timeGridPlugin,
          dayGridPlugin,
          bootstrapPlugin,
        ],

        // Default settings for FullCalendar
        themeSystem: "bootstrap",
        eventDisplay: "block",
        initialView: "timeGridWeek",
        locale: plLocale,
        timeZone: "UTC",
        height: "auto",

        // Allow clicking in day and week names, determine time range displayed
        navLinks: true,
        allDaySlot: false,
        slotMinTime: "08:00:00",
        slotMaxTime: "22:00:00",

        // Define which buttons should be displayed for navigation
        headerToolbar: {
          start: "prev,next today",
          center: "title",
          end: "timeGridDay,timeGridWeek,dayGridMonth",
        },

        // buttonText is a text displayed in "prev" and "next" keys
        buttonText: {
          prev: "\u25C1",
          next: "\u25B7",
        },

        // Display date in format day - full month name - year
        titleFormat: {
          day: "numeric",
          month: "long",
          year: "numeric",
        },

        // events are fetched from database using function fetchEvents
        events: this.fetchEvents,

        // Allow for selecting hours in the calendar to create events, print
        // the block showing that event. 'select' and 'eventClick' are
        // references to Vue app 'reservation' functions for creating and
        // editing/viewing events.
        selectable: true,
        selectMirror: true,

        select: this.showCreateModal,
        eventClick: this.showEditViewModal,
      },
    };
  },
  methods: {
    fetchEvents: async function (fetchInfo) {
      let url = new URL("classrooms/terms/", window.location.origin);
      url.searchParams.set("start", fetchInfo.start.toISOString());
      url.searchParams.set("end", fetchInfo.end.toISOString());

      let usp = this.$refs.filtersComponent.create_searchparams();
      for (const [key, value] of usp)
        url.searchParams.set(key, value);

      let events = [];
      await axios.get(url.toString()).then((r) => {
        for (let term of r.data) {
          // Set colors for fetched events: based on type, color the box of the
          // event, based on the status. If event is invisible, it has its own
          // color, no matter what type it has. It also have the priority over
          // event types. Pending events (status 0) are marked with stripes,
          // accepted events (status 1) are marked with solid color, rejected
          // events (status 2) are transparent.
          Array.prototype.map.call(term["type"], (type) => {
            term["color"] = event_type_map[type];
          });

          if (!term["visible"])
            term["color"] = "#D3BB5A";

          if (term["status"] == 0)
            term["className"] = ["progress-bar-striped"];

          if (term["status"] == 2)
            term["color"] = convertHexToRGBA(term["color"], 50);

          events.push(term);
        }
      });

      return events;
    },

    showCreateModal(timeRange) {
      this.$refs.reservationComponent.show_modal_add(timeRange);
    },

    showEditViewModal(info) {
      this.$refs.reservationComponent.show_modal_edit_or_view(info);
    },

    refetchEvents() {
      this.$refs.calendarComponent.getApi().refetchEvents();
    },

    addEvent(event) {
      this.$refs.calendarComponent.getApi().addEvent(event);
    },

    unselect() {
      this.$refs.calendarComponent.getApi().unselect();
    },

    hideEventById(event_id) {
      let event = this.$refs.calendarComponent.getApi().getEventById(event_id);
      if (event) event.remove();
    },
  },
};
</script>
