<template>
  <div>
    <div
      class="modal fade"
      tabindex="-1"
      role="dialog"
      id="reservation_modal"
      ref="modal_ref"
    >
      <div class="modal-dialog modal-lg modal-dialog-centered" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 v-if="!edit_or_view" class="modal-title">Utwórz wydarzenie</h5>
            <h5
              v-else-if="edit_or_view && user_has_permissions()"
              class="modal-title"
            >
              Edytuj wydarzenie
            </h5>
            <h5 v-else class="modal-title">Informacje o wydarzeniu</h5>
            <button type="button" class="close" data-dismiss="modal">
              <span>&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <div
              class="alert alert-danger alert-message"
              role="alert"
              v-if="show_alert"
            >
              {{ error_message }}
            </div>
            <fieldset :disabled="edit_or_view && !user_has_permissions()">
              <div class="form-group" v-if="edit_or_view">
                <label for="author">Autor wydarzenia</label>
                <input
                  type="text"
                  class="form-control"
                  id="author"
                  v-model="author"
                  disabled
                />
              </div>

              <div class="form-group">
                <label for="name">Nazwa wydarzenia</label>
                <input
                  class="form-control"
                  placeholder="Seminarium ANL"
                  id="name"
                  v-model="name"
                />
              </div>

              <div class="form-group">
                <label for="description">Opis wydarzenia</label>
                <textarea
                  class="form-control"
                  placeholder="Co będzie się działo?"
                  id="description"
                  v-model="description"
                ></textarea>
              </div>

              <div class="form-group" v-if="field_is_editable()">
                <label for="visibility"
                  >Wydarzenie widoczne dla wszystkich użytkowników</label
                >
                <select v-model="visible" class="form-control" id="visibility">
                  <option
                    v-for="option in options.visible"
                    v-bind:value="option.value"
                    v-bind:key="option.value"
                  >
                    {{ option.text }}
                  </option>
                </select>
              </div>

              <div
                class="form-group"
                v-if="
                  edit_or_view || user_info.is_admin || user_info.is_employee
                "
              >
                <label for="type">Typ wydarzenia</label>
                <select
                  id="type"
                  class="form-control"
                  v-model="type"
                  v-bind:disabled="
                    !(user_info.is_admin || user_info.is_employee)
                  "
                >
                  <option
                    v-for="option in options.type"
                    v-bind:value="option.value"
                    v-bind:key="option.value"
                    v-bind:disabled="option.value === '5'"
                  >
                    {{ option.text }}
                  </option>
                </select>
              </div>

              <div
                class="form-group"
                v-if="edit_or_view && user_has_permissions()"
              >
                <label for="status">Status wydarzenia</label>
                <select
                  id="status"
                  class="form-control"
                  v-model="status"
                  v-bind:disabled="!user_info.is_admin"
                >
                  <option
                    v-for="option in options.status"
                    v-bind:value="option.value"
                    v-bind:key="option.value"
                  >
                    {{ option.text }}
                  </option>
                </select>
              </div>

              <table class="table">
                <thead>
                  <tr>
                    <td class="align-middle"><strong>Dzień</strong></td>
                    <td class="align-middle"><strong>Początek</strong></td>
                    <td class="align-middle"><strong>Koniec</strong></td>
                    <td class="align-middle"><strong>Miejsce</strong></td>
                    <td class="align-middle" v-if="field_is_editable()"></td>
                    <td v-if="field_is_editable()"></td>
                  </tr>
                </thead>
                <tbody>
                  <TermSelection
                    v-for="(term, index) in terms"
                    v-bind:key="index"
                    v-bind:term="term"
                    v-bind:termIndex="index"
                    v-bind:canEdit="field_is_editable()"
                    v-bind:allRooms="options.rooms"
                    v-bind:event="id"
                    v-on:removeTerm="removeTerm"
                  >
                  </TermSelection>
                </tbody>
              </table>
              <div v-if="field_is_editable()">
                <button class="btn btn-primary" @click="add_term">
                  Dodaj termin
                </button>
              </div>
            </fieldset>
          </div>
          <div class="modal-footer" v-if="!edit_or_view">
            <button
              type="button"
              class="btn btn-secondary"
              data-dismiss="modal"
            >
              Anuluj
            </button>
            <button
              type="button"
              class="btn btn-success"
              @click="check_inputs_and_add_to_db"
            >
              Utwórz wydarzenie
            </button>
          </div>
          <div
            class="modal-footer"
            v-else-if="edit_or_view && user_has_permissions()"
          >
            <button
              type="button"
              class="btn btn-secondary"
              data-dismiss="modal"
            >
              Anuluj
            </button>
            <button
              type="button"
              class="btn btn-danger"
              @click="remove_from_db(url)"
            >
              Usuń wydarzenie
            </button>
            <button
              type="button"
              class="btn btn-success"
              @click="check_inputs_and_edit_in_db"
            >
              Edytuj wydarzenie
            </button>
          </div>
          <div class="modal-footer" v-else>
            <button
              type="button"
              class="btn btn-secondary"
              data-dismiss="modal"
            >
              Anuluj
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import dayjs from "dayjs";
import Vue from "vue";
import TermSelection from "./TermSelection";
const utc = require("dayjs/plugin/utc");
const isSameOrAfter = require("dayjs/plugin/isSameOrAfter");
const customParseFormat = require("dayjs/plugin/customParseFormat");
dayjs.extend(utc);
dayjs.extend(isSameOrAfter);
dayjs.extend(customParseFormat);

axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";
axios.defaults.xsrfCookieName = "csrftoken";

export default {
  name: "Reservation",
  components: {
    TermSelection,
  },
  data() {
    return {
      author: "",
      name: "",
      description: "",
      visible: true,
      type: "2",
      status: "0",
      terms: [],

      options: {
        visible: [
          { value: true, text: "Tak" },
          { value: false, text: "Nie" },
        ],
        type: [
          { value: "0", text: "Egzamin" },
          { value: "1", text: "Kolokwium" },
          { value: "2", text: "Wydarzenie" },
          { value: "5", text: "Rezerwacja cykliczna" },
        ],
        status: [
          { value: "0", text: "Oczekujące" },
          { value: "1", text: "Zaakceptowane" },
          { value: "2", text: "Odrzucone" },
        ],
        rooms: [],
      },

      edit_or_view: false,
      show_alert: false,
      error_message: "",

      id : null,
      url: "",
      user_info: {
        full_name: "",
        is_student: false,
        is_employee: false,
        is_admin: false,
      },
    };
  },
  mounted() {
    // If reservation modal closes by any way, reload all modal's data and remove
    // temporary event in calendar (used on creating events)
    $(this.$refs.modal_ref).on("hidden.bs.modal", this.clear_and_hide_modal);
  },
  created: function () {
    this.fetch_data_from_html();
  },
  methods: {
    removeTerm(termIndex) {
      this.terms.splice(termIndex, 1);
    },
    fetch_data_from_html: function () {
      // Data for classrooms and user is sent by Django templates, thus we need
      // to retrieve it and save it, so we can use it everywhere in this component.
      this.options.rooms = JSON.parse(
        document.getElementById("classrooms").innerHTML
      );
      this.user_info = JSON.parse(
        document.getElementById("user_info").innerHTML
      );
    },

    // Functions with fc_ prefix are shorthands for emitting methods in the
    // Fullcalendar component, as it is the only possibility to call them.
    fc_add_event: function (event_obj) {
      this.$emit("addEvent", event_obj);
    },

    fc_unselect: function () {
      this.$emit("unselect");
    },

    fc_hide_event_by_id: function (event_id) {
      this.$emit("hideEventById", event_id);
    },

    fc_refetch_events: function () {
      this.$emit("refetchEvents");
    },

    user_has_permissions: function () {
      return this.user_info.is_admin || this.user_info.full_name == this.author;
    },

    field_is_editable: function () {
      // Editable fields are visible only when user wants to create event or
      // when user has permissions to edit it (is admin or event author).
      return !this.edit_or_view || this.user_has_permissions();
    },

    // This modal is displayed only when adding event, it supports either adding events
    // by clicking the "Create event" button and selecting hours in FullCalendar
    show_modal_add: function (timeRange) {
      this.clear_modal();
      this.edit_or_view = false; // do not print extra fields (available in edit/view modes only)
      $("#reservation_modal").modal("show");

      if (timeRange != null) {
        // timeRange is argument received from FullCalendar by selecting event's hours
        let start = new Date(timeRange.startStr).toISOString();
        let end = new Date(timeRange.endStr).toISOString();

        this.add_term();
        // Get the day in YYYY-MM-DD format and start and end in HH-MM format
        this.terms[0].day = dayjs(start).format("YYYY-MM-DD");
        this.terms[0].start = dayjs(start).utc().format("HH:mm");
        this.terms[0].end = dayjs(end).utc().format("HH:mm");

        // If user wants to make a reservation in "Month" view, startStr and endStr
        // are equal to 00:00, so make the term to be since 8 AM to 10 PM.
        if (this.terms[0].start == "00:00") this.terms[0].start = "08:00";
        if (this.terms[0].end == "00:00") this.terms[0].end = "22:00";

        // Display temporary event in the calendar which corresponds to selected hours
        this.fc_add_event({
          id: "temp",
          title: "Nowe wydarzenie (wstępny termin)",
          start: start,
          end: end,
          color: "pink",
        });
        this.fc_unselect();
      }
    },

    // This modal is used both in editing an event and displaying its properties
    // (for people without permissions), it is opened by clicking an event in calendar.
    show_modal_edit_or_view: async function (info) {
      // When user wants to see properties of classes, return from the function
      // and user will be redirected to the group's list.
      if (info.event.url.includes("course")) return;

      this.clear_modal();
      this.edit_or_view = true;
      info.jsEvent.preventDefault();

      // Get data from given URL and save it in fields of reservation app.
      await axios.get(info.event.url).then((event) => {
        this.author = event.data.author;
        this.name = event.data.title;
        this.description = event.data.description;
        this.type = event.data.type;
        this.status = event.data.status;
        this.visible = event.data.visible;
        this.url = event.data.url;
        this.id = event.data.id;

        for (let term of event.data.terms) {
          // We need to get rid of seconds to send data properly (expected format
          // is HH:MM, but fetched data is in format HH:MM:SS).
          term.start = dayjs(term.start, "HH:mm").format("HH:mm");
          term.end = dayjs(term.end, "HH:mm").format("HH:mm");

          term.ignore_conflicts = !(
            term.ignore_conflicts_rooms == null || !term.ignore_conflicts_rooms
          );
        }
        this.terms = event.data.terms;
      });

      $("#reservation_modal").modal("show");
    },

    // Empty all data fields used in the form and close the modal, used basically
    // to prepare the modal for next uses.
    clear_and_hide_modal: async function () {
      this.fc_hide_event_by_id("temp");
      await this.fc_refetch_events();

      this.author = "";
      this.name = "";
      this.description = "";
      this.type = "2";
      this.status = "0";
      this.visible = true;
      this.terms = [];
      this.url = "";

      $("#reservation_modal").modal("hide");
    },

    clear_modal: function () {
      this.author = "";
      this.name = "";
      this.description = "";
      this.type = "2";
      this.status = "0";
      this.visible = true;
      this.terms = [];
      this.error_message = "";
      this.show_alert = false;
      this.url = "";
    },

    hide_modal: function () {
      $("#reservation_modal").modal("hide");
    },

    // Add a term row in the add/edit event modal
    add_term: function () {
      this.terms.push({
        day: "",
        start: "",
        end: "",
        place: "",
        rooms: {},
        // ignore_conflicts: false,
        // ignore_conflicts_rooms: [],
      });
    },

    // Remove a term row from in the add/edit event modal
    remove_term: function (index) {
      this.terms.splice(index, 1);
      // this.original_terms.splice(index, 1);
    },

    check_inputs: function () {
      if (this.name && this.description) return true;

      let errors = "";
      if (!this.name) errors += "Nie wprowadzono nazwy wydarzenia.\n";

      if (!this.description) errors += "Nie wprowadzono opisu wydarzenia.\n";

      this.error_message = errors;
      this.show_alert = true;
      return false;
    },

    // Send reservation's data in POST request, so it gets saved in database.
    add_to_db: async function () {
      let that = this; // without it, closing modal without errors is impossible
      await axios
        .post("events/", {
          title: this.name,
          description: this.description,
          visible: this.visible,
          type: this.type,
          terms: this.terms,
        })
        .then(function (response) {
          that.hide_modal();
        })
        .catch(function (error) {
          that.show_alert = true;
          if (error.response.status == 400) {
            if (
              Array.isArray(error.response.data) &&
              error.response.data.length
            ) {
              // returned JSON with conflicts
              let conflicts = "";
              for (const conflict of error.response.data)
                conflicts +=
                  '\nWydarzenie "' +
                  conflict.title +
                  '" w sali ' +
                  conflict.room +
                  " od " +
                  conflict.start +
                  " do " +
                  conflict.end;

              that.error_message =
                "Nie udało się utworzyć wydarzenia. Nastąpiły konflikty z:" +
                conflicts;
            } // otherwise some term is not filled completely
            else that.error_message = "Któryś z termów jest nieuzupełniony.";
          }
        });
    },

    check_inputs_and_add_to_db: function () {
      if (this.check_inputs()) this.add_to_db();
    },

    // Send edited reservation's data in POST
    edit_in_db: async function () {
      // If user who is not an admin tries to edit an event, its status has to be
      // changed to "pending" - otherwise unprivileged users would not be able to
      // edit events created by them.
      let that = this;
      await axios
        .post(this.url, {
          title: this.name,
          description: this.description,
          visible: this.visible,
          status: this.user_info.is_admin ? this.status : "0",
          type: this.type,
          terms: this.terms,
        })
        .then(function (response) {
          that.hide_modal();
        })
        .catch(function (error) {
          that.show_alert = true;
          if (error.response.status == 400) {
            if (
              Array.isArray(error.response.data) &&
              error.response.data.length
            ) {
              // returned JSON with conflicts
              let conflicts = "";
              for (const conflict of error.response.data)
                conflicts +=
                  '\nWydarzenie "' +
                  conflict.title +
                  '" w sali ' +
                  conflict.room +
                  " od " +
                  conflict.start +
                  " do " +
                  conflict.end;

              that.error_message =
                "Nie udało się utworzyć wydarzenia. Nastąpiły konflikty z:" +
                conflicts;
            } // otherwise some term is not filled completely
            else that.error_message = "Któryś z termów jest nieuzupełniony.";
          }
        });
    },

    check_inputs_and_edit_in_db: function () {
      if (this.check_inputs()) this.edit_in_db();
    },

    // Remove event with given URL from database
    remove_from_db: async function (url) {
      if (!url) return;

      await axios.post("delete-event/" + parseInt(url.match(/\d+/)) + "/");
      this.hide_modal();
    },
  },
};
</script>