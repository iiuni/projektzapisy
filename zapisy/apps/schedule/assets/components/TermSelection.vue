<template>
  <tr>
    <td><input class="form-control" type="date" v-model="term.day" /></td>
    <td>
      <input
        class="form-control"
        type="time"
        step="60"
        min="08:00"
        max="22:00"
        v-model="term.start"
      />
    </td>
    <td>
      <input
        class="form-control"
        type="time"
        step="60"
        min="08:00"
        max="22:00"
        v-model="term.end"
      />
    </td>
    <td>
      <div class="dropdown dropup" v-if="canEdit">
        <button
          class="btn btn-secondary dropdown-toggle"
          type="button"
          id="dropdownMenuButton"
          data-toggle="dropdown"
          aria-haspopup="true"
          aria-expanded="false"
        >
          Wybierz
        </button>

        <div
          class="dropdown-menu scrollable-menu"
          aria-labelledby="dropdownMenuButton"
        >
          <div class="dropdown-item" v-bind:class="{ active: term.place }">
            Miejsce poza instytutem
          </div>
          <input
            type="text"
            class="form-control"
            v-model="term.place"
            placeholder="Sala HS w Instytucie Matematyki"
          />

          <button
            class="dropdown-item term"
            style="
              outline: none;
              border: 1px solid black;
              max-height: 60px !important;
            "
            v-for="room in allRooms"
            v-bind:key="room.number"
            v-bind:class="{
              active: isReserved(room.number),
            }"
            v-on:click="toggleRoomReservation(room.number)"
          >
            <div class="progress bg-light term-bar" style="height: 14px">
              <div
                role="progressbar"
                class="progress-bar"
                v-for="(b, idx) in conflictBarElements(room.number)"
                v-bind:key="idx"
                v-bind:class="b.color"
                v-bind:style="{ width: b.width }"
              ></div>
            </div>
            <div class="row" style="font-family: monospace">
              <div
                class="d-flex flex-row justify-content-between"
                style="width: 100%"
              >
                <div>08:00</div>
                <div>10:00</div>
                <div>12:00</div>
                <div>14:00</div>
                <div>16:00</div>
                <div>18:00</div>
                <div>20:00</div>
                <div>22:00</div>
              </div>
            </div>
            <div>
              {{ room.number }} ({{ room.capacity }} miejsc, {{ room.type }})
            </div>
          </button>
        </div>
      </div>
      <div>
        Sale:
        <p
          v-for="(_, number) in term.rooms"
          :key="number"
          style="display: inline"
        >
          {{ number }}
        </p>
      </div>
      <div v-if="term.place">
        Miejsce poza II:
        {{ term.place }}
      </div>
    </td>
    <td>
      <button
        class="btn btn-info"
        data-toggle="collapse"
        style="margin-bottom: 5px"
        :data-target="'#conflicts' + termIndex"
      >
        Konflikty
      </button>

      <div :id="'conflicts' + termIndex" class="collapse">
        <div v-for="(_, number) in term.rooms" v-bind:key="number">
          <input type="checkbox" v-model="term.rooms[number]" />
          <label>{{ number }}</label>
        </div>
      </div>
    </td>
    <td v-if="canEdit">
      <button v-on:click="removeTerm" class="btn btn-danger">-</button>
    </td>
  </tr>
</template>

<script lang=ts>
import Vue, { PropType } from "vue";
import _ from "lodash";
import axios from "axios";

interface RoomDescription {
  number: string;
  capacity: number;
  type: string;
}

interface Term {
  rooms: Record<string, boolean>;
  place: string;
  day: string;
  start: string;
  end: string;
}

const totalTime = (22 - 8) * 60;

function parseTime(time: string) {
  let [h, m] = time.split(":");
  return 60 * Number(h) + Number(m);
}

function toPercentage(minutes: number) {
  return ((minutes / totalTime) * 100).toFixed(2) + "%";
}

const enum Action {
  StartOther,
  EndOther,
  StartTerm,
  EndTerm,
}

function mkEvent(time: string, act: Action) {
  return { time: parseTime(time), act };
}

export default Vue.extend({
  props: {
    // since objects are passed by reference we can directly mutate state passed by prop
    term: Object as PropType<Term>,
    termIndex: Number,
    canEdit: Boolean,
    allRooms: Array as PropType<RoomDescription[]>,
    event: Number,
  },
  data() {
    return {
      otherReservations: {} as Record<string, [string, string][]>,
    };
  },
  watch: {
    "term.day": function (day) {
      this.getOtherReservations(day);
    },
  },
  created() {
    this.getOtherReservations(this.term.day);
  },
  methods: {
    async getOtherReservations(day: string) {
      let url = new URL(
        "classrooms/chosen-days-terms/",
        window.location.origin
      );
      url.searchParams.append("days", day);
      if (this.event != null) {
        url.searchParams.append("event", this.event.toString());
      }
      await axios
        .get(url.toString())
        .then(({ data }) => (this.otherReservations = data));
    },
    isReserved(number: string) {
      return number in this.term.rooms;
    },
    toggleRoomReservation(number: string) {
      if (number in this.term.rooms) {
        Vue.delete(this.term.rooms, number)
      } else {
        Vue.set(this.term.rooms, number, false);
      }
    },
    removeTerm() {
      this.$emit("removeTerm", this.termIndex);
    },
    conflictBarElements(roomNumber: string) {
      let intervals = this.otherReservations[roomNumber];
      if (!intervals) intervals = [];
      let events = [];
      for (let [start, end] of intervals) {
        events.push(
          mkEvent(start, Action.StartOther),
          mkEvent(end, Action.EndOther)
        );
      }
      let startTerm = mkEvent(this.term.start, Action.StartTerm);
      let endTerm = mkEvent(this.term.end, Action.EndTerm);
      let start = _.sortedLastIndexBy(events, startTerm, "time");
      events.splice(start, 0, startTerm);
      let end = _.sortedLastIndexBy(events, endTerm, "time");
      events.splice(end, 0, endTerm);

      let elements = [];
      let current = 8 * 60; // 8:00
      let inOther = false;
      let inTerm = false;
      for (let { time, act } of events) {
        let color = "";
        switch (act) {
          case Action.StartOther:
            color = inTerm ? "bg-success" : "bg-transparent";
            inOther = true;
            break;
          case Action.StartTerm:
            color = inOther ? "bg-secondary" : "bg-transparent";
            inTerm = true;
            break;
          case Action.EndOther:
            color = inTerm ? "bg-danger" : "bg-secondary";
            inOther = false;
            break;
          case Action.EndTerm:
            color = inOther ? "bg-danger" : "bg-success";
            inTerm = false;
            break;
        }
        if (color && current < time)
          elements.push({ width: toPercentage(time - current), color });
        current = time;
      }
      return elements;
    },
  },
});
</script>

<style scoped>
.dropdown-item.term.active {
  background: #2aabd2;
}

.scrollable-menu {
  height: auto;
  max-height: 400px;
  overflow-x: hidden;
}

.dropdown:hover .dropdown-menu {
  white-space: nowrap;
  display: block;
  margin-bottom: 0; /* remove the gap so it doesn't close */
}

.alert-message {
  white-space: pre;
}
</style>