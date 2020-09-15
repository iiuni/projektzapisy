const path = require("path");

const AssetDefs = {
  // Common app

  "common-main": [
    path.resolve("apps/common/assets/main/expose_libs.ts"),
    path.resolve("apps/common/assets/main/_variables.scss"),
    path.resolve("apps/common/assets/main/index.scss"),
    path.resolve("apps/common/assets/cookieconsent/display-cookieconsent.ts"),
    path.resolve("apps/common/assets/main/icons-library.js"),
    path.resolve("apps/common/assets/main/sidebar-fold.js"),
  ],
  "common-render-markdown": [
    path.resolve("apps/common/assets/markdown/render-markdown.ts"),
    path.resolve("apps/common/assets/markdown/render-markdown.scss"),
  ],
  "common-markdown-editor": [
    path.resolve("apps/common/assets/markdown/markdown-editor.js"),
  ],

  // Courses app

  "courses-course-list": [
    path.resolve("apps/enrollment/courses/assets/course-list-index.js"),
  ],

  // Timetable app

  "timetable-timetable-component": [
    path.resolve("apps/enrollment/timetable/assets/simple-timetable-index.js"),
  ],
  "timetable-prototype-component": [
    path.resolve("apps/enrollment/timetable/assets/prototype-index.js"),
  ],
  "timetable-prototype-legend-stylesheet": [
    path.resolve("apps/enrollment/timetable/assets/prototype-legend.scss"),
  ],

  // Poll app

  "poll-bokeh-plotting": [path.resolve("apps/grade/poll/assets/bokeh.js")],

  // Ticket_create app

  "ticket_create-katex": [
    path.resolve("apps/grade/ticket_create/assets/katex.ts"),
  ],
  "ticket_create-ticketsgenerate": [
    path.resolve("apps/grade/ticket_create/assets/ticketsgenerate_main.js"),
  ],

  // Notification app

  "notifications-notifications-widget": [
    path.resolve("apps/notifications/assets/notifications-widget.js"),
  ],

  // Desiderata app

  "desiderata-checkboxes": [
    path.resolve("apps/offer/desiderata/assets/checkboxes-toggling.js"),
  ],

  // Proposal app

  "proposal-course-list": [
    path.resolve("apps/offer/proposal/assets/course-list-index.js"),
  ],

  // Vote app

  "vote-point-counter": [
    path.resolve("apps/offer/vote/assets/point-counter.ts"),
  ],
  "vote-bootstrap-table": [
    path.resolve("apps/offer/vote/assets/bootstrap-table.js"),
  ],

  // Schedule app

  "schedule-reservation-widget": [
    path.resolve("apps/schedule/assets/reservation-widget.js"),
  ],
  "schedule-reservation": [path.resolve("apps/schedule/assets/reservation.js")],
  "schedule-fullcalendar": [
    path.resolve("apps/schedule/assets/fullcalendar.js"),
    path.resolve("apps/schedule/assets/fullcalendar.scss"),
  ],
  "schedule-report": [
    path.resolve("apps/schedule/assets/report.js"),
    path.resolve("apps/schedule/assets/report.css"),
  ],
  "schedule-report-editor": [
    path.resolve("apps/schedule/assets/report-editor.js"),
    path.resolve("apps/schedule/assets/report-editor.scss"),
  ],

  // Theses app

  "theses-theses-widget": [path.resolve("apps/theses/assets/theses-widget.js")],

  // User app

  "users-user-filter": [
    path.resolve("apps/users/assets/user-filter-list-index.js"),
  ],
  "users-consent-dialog": [path.resolve("apps/users/assets/consent-dialog.ts")],
};

module.exports = AssetDefs;
