<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import $ from "jquery";
import { min, max } from "lodash";
import axios from "axios";
import { TermDisplay, Classroom, isFree, calculateLength } from "../terms";
import ClassroomField from "./ClassroomField.vue";

const ClassroomPickerDefinition = Vue.extend({
  components: {
    ClassroomField,
  },
  data: () => {
    return {
      showOccupied: true,
    };
  },
});

@Component
export default class ClassroomPicker extends ClassroomPickerDefinition {
  classrooms: Classroom[] = [];
  unoccupiedClassrooms: Classroom[] = [];
  reservationLayer: TermDisplay[] = [];

  // Attaches handlers to change of active term form.
  mounted() {
    let self = this;

    // Sets handlers to change of time and date for currently
    // active term.
    let f = (event: Event) => {
      self.onChangedTime();
      self.onChangedDate();

      $(".active-term").find(".form-time").on("change", self.onChangedTime);

      $(".active-term").find(".form-day").on("change", self.onChangedDate);
    };

    // The only two ways to change active term is clicking on
    // edit term form or new term form, so we set handlers to
    // the click events on all of these buttons in the document.
    $(document).on("click", ".edit-term-form", f);
    $(document).on("click", "#new-term-form", f);
  }

  getUnoccupied() {
    let begin = $(".active-term").find(".form-start").val() as string;
    let end = $(".active-term").find(".form-end").val() as string;
    this.unoccupiedClassrooms = this.classrooms.filter((item) => {
      return isFree(item.rawOccupied, begin, end);
    });
  }

  onChangedTime() {
    let start = $(".active-term").find(".form-start").val() as string;
    let end = $(".active-term").find(".form-end").val() as string;

    if (start > end || end < "08:00" || start > "22:00") {
      this.reservationLayer = [];
      return;
    }

    start = max(["08:00", start]) as string;
    end = min(["22:00", end]) as string;

    this.getUnoccupied();

    this.reservationLayer = [];
    this.reservationLayer.push({
      width: calculateLength("08:00", start),
      occupied: false,
    });
    this.reservationLayer.push({
      width: calculateLength(start, end),
      occupied: true,
    });
    this.reservationLayer.push({
      width: calculateLength(end, "22:00"),
      occupied: false,
    });
  }

  onChangedDate() {
    var self = this;
    var date = $(".active-term").find(".form-day").val();

    if (date === "") {
      self.classrooms = [];
      self.unoccupiedClassrooms = [];
      return;
    }

    axios.get("/classrooms/get_terms/" + date + "/").then((response) => {
      self.classrooms = [];
      for (let key in response.data) {
        let item = response.data[key];
        let termsLayer = [];

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

        self.classrooms.push({
          label: item.number,
          type: item.type,
          id: item.id,
          capacity: item.capacity,
          termsLayer: termsLayer,
          rawOccupied: item.occupied,
        });
      }
      self.getUnoccupied();
    });
  }
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
      v-for="item in showOccupied ? this.classrooms : this.unoccupiedClassrooms"
      :key="item.id"
      :label="item.label"
      :capacity="item.capacity"
      :id="item.id"
      :type="item.type"
      :termsLayer="item.termsLayer"
      :reservationLayer="reservationLayer"
    />
  </div>
</template>
