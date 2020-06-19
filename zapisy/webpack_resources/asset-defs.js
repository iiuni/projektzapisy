const path = require("path");

const AssetDefs = {
  // Common app

  "common-main": [
    path.resolve("apps/common/assets/main/expose_libs.ts"),
    path.resolve("apps/common/assets/main/_variables.scss"),
    path.resolve("apps/common/assets/main/index.scss"),
    path.resolve(
      "apps/common/assets/cookieconsent/display-cookieconsent.ts"
    ),
    path.resolve(
      "apps/common/assets/main/icons-library.ts"
    ),
    path.resolve("apps/common/assets/main/sidebar-fold.js"),
  ],

  // Courses app

  "courses-course-list": [
    path.resolve(
      "apps/enrollment/courses/assets/course-list-index.js"
    ),
  ],

  // Timetable app

  "timetable-timetable-component": [
    path.resolve(
      "apps/enrollment/timetable/assets/simple-timetable-index.js"
    ),
  ],
  "timetable-prototype-component": [
    path.resolve(
      "apps/enrollment/timetable/assets/prototype-index.js"
    ),
  ],
  "timetable-prototype-legend-stylesheet": [
    path.resolve(
      "apps/enrollment/timetable/assets/prototype-legend.scss"
    ),
  ],

  // Poll app

  "poll-bokeh-plotting": ["bokeh.js", "bokeh.scss"],

  // Ticket_create app

  "ticket_create-katex": [
    "apps/grade/ticket_create/assets/katex.ts",
  ],
  "ticket_create-ticketsgenerate": [
    "apps/grade/ticket_create/assets/ticketsgenerate_main.js",
  ],

  // Notification app

  "notifications-notifications-widget": [
    "apps/notifications/assets/notifications-widget.js",
  ],

  // Desiderata app

  "desiderata-checkboxes": [
    "apps/offer/desiderata/assets/checkboxes-toggling.js",
  ],

  // Proposal app

  "proposal-fill-placeholders": [
    "apps/offer/proposal/assets/fill-placeholders.ts",
  ],
  "proposal-course-list": [
    "apps/offer/proposal/assets/course-list-index.js",
  ],

  // Vote app

  "vote-point-counter": [
    "apps/offer/vote/assets/point-counter.ts",
  ],
  "vote-bootstrap-table": [
    "apps/offer/vote/assets/bootstrap-table.js",
  ],

  // Schedule app

  "schedule-reservation-widget": [
    "apps/schedule/assets/reservation-widget.js",
  ],
  "schedule-reservation": [
    "apps/schedule/assets/reservation.js",
  ],
  "schedule-fullcalendar": [
    "apps/schedule/assets/fullcalendar.ts",
  ],
  "schedule-report": [
    "apps/schedule/assets/report.js",
    "apps/schedule/assets/report.css",
  ],
  "schedule-report-editor": [
    "apps/schedule/assets/report-editor.ts",
    "apps/schedule/assets/report-editor.scss",
  ],

  // Theses app

  "theses-theses-widget": [
    "apps/theses/assets/theses-widget.js",
  ],

  // User app

  "user-user-filter": [
    "apps/user/assets/user-filter-list-index.js",
  ],
  "user-consent-dialog": [
    "apps/user/assets/consent-dialog.ts",
  ],
};

module.exports = AssetDefs;
