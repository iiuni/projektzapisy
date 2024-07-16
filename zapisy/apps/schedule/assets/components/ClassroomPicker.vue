<script setup lang="ts">
import $ from "jquery";
import { min, max } from "lodash";
import axios from "axios";
import { TermDisplay, Classroom, isFree, calculateLength } from "../terms";
import ClassroomField from "./ClassroomField.vue";
import { ref, onMounted } from "vue";

const showOccupied = ref(false);

const classrooms = ref<Classroom[]>([]);
const unoccupiedClassrooms = ref<Classroom[]>([]);
const reservationLayer = ref<TermDisplay[]>([]);

// Attaches handlers to change of active term form.
onMounted(() => {
  // let self = this;
  // Sets handlers to change of time and date for currently
  // active term.
  let f = (event: Event) => {
    onChangedTime();
    onChangedDate();

    $(".active-term").find(".form-time").on("change", onChangedTime);

    $(".active-term").find(".form-day").on("change", onChangedDate);
  };

  // Vanilla JS give us know when change active term
  document.addEventListener("refresh-classroom-picker", f);
});

function getUnoccupied() {
  let begin = $(".active-term").find(".form-start").val() as string;
  let end = $(".active-term").find(".form-end").val() as string;
  unoccupiedClassrooms.value = classrooms.value.filter((item) => {
    return isFree(item.rawOccupied, begin, end);
  });
}

function onChangedTime() {
  let start = $(".active-term").find(".form-start").val() as string;
  let end = $(".active-term").find(".form-end").val() as string;

  if (start > end || end < "08:00" || start > "22:00") {
    reservationLayer.value = [];
    return;
  }

  start = max(["08:00", start]) as string;
  end = min(["22:00", end]) as string;

  getUnoccupied();

  reservationLayer.value = [];
  reservationLayer.value.push({
    width: calculateLength("08:00", start),
    occupied: false,
  });
  reservationLayer.value.push({
    width: calculateLength(start, end),
    occupied: true,
  });
  reservationLayer.value.push({
    width: calculateLength(end, "22:00"),
    occupied: false,
  });
}

function onChangedDate() {
  // var self = this;
  var date = $(".active-term").find(".form-day").val();

  if (date === "") {
    classrooms.value = [];
    unoccupiedClassrooms.value = [];
    return;
  }

  axios.get("/classrooms/get_terms/" + date + "/").then((response) => {
    classrooms.value = [];
    for (let key in response.data) {
      let item = response.data[key];
      let termsLayer: { width: string; occupied: boolean }[] = [];

      item.occupied.push({
        begin: "22:00",
      });
      let lastFree = "08:00";

      for (const occ of item.occupied) {
        const emptyWidth = calculateLength(lastFree, occ.begin);
        termsLayer.push({
          width: emptyWidth,
          occupied: false,
        });
        if (!occ.end) {
          // We reached the last, dummy event.
          break;
        }
        let width = calculateLength(occ.begin, occ.end);
        termsLayer.push({
          width: width,
          occupied: true,
        });
        lastFree = occ.end;
      }

      classrooms.value.push({
        label: item.number,
        type: item.type,
        id: item.id,
        capacity: item.capacity,
        termsLayer: termsLayer,
        rawOccupied: item.occupied,
      });
    }
    getUnoccupied();
  });
}
</script>

<template>
  <div>
    <h3>Filtruj sale</h3>
    <div class="input-group">
      <div class="custom-control custom-checkbox">
        <input
          type="checkbox"
          class="custom-control-input"
          id="showOccupied"
          v-model="showOccupied"
        />
        <label class="custom-control-label" for="showOccupied"
          >Pokaż zajęte</label
        >
      </div>
    </div>
    <ClassroomField
      v-for="item in showOccupied ? classrooms : unoccupiedClassrooms"
      :key="item.id.toString()"
      :label="item.label.toString()"
      :capacity="Number(item.capacity)"
      :id="Number(item.id)"
      :type="item.type.toString()"
      :termsLayer="item.termsLayer"
      :reservationLayer="reservationLayer"
    />
  </div>
</template>
