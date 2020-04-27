<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import $ from "jquery";
import axios from "axios";
import { Term, Classroom, calculateLength } from "../store/terms";
import ClassroomField from "./ClassroomField.vue";

@Component({
  components: {
    ClassroomField
  }
})
export default class ClassroomPicker extends Vue {
  classrooms: Classroom[] = [];

  reservationLayer: Term[] = [];

  mounted() {
    let self = this;
    $(".form-time").change(function(event) {
      let start = $("#start-time").val();
      let end = $("#end-time").val();

      self.reservationLayer = [];
      self.reservationLayer.push({
        width: calculateLength("08:00", start),
        occupied: false
      });
      self.reservationLayer.push({
        width: calculateLength(start, end),
        occupied: true
      });
      self.reservationLayer.push({
        width: calculateLength(end, "22:00"),
        occupied: false
      });
    });

    $(".form-date").change(function(event) {
      var date = $(".form-date")
        .val()
        .split("-");

      axios
        .get(
          "/classrooms/get_terms/" +
            date[0] +
            "/" +
            date[1] +
            "/" +
            date[2] +
            "/"
        )
        .then(response => {
          self.classrooms = [];
          for (let key in response.data) {
            let item = response.data[key];
            let termsLayer = [];

            if (item.occupied.length != 0) {
              let width = calculateLength("08:00", item.occupied[0].begin);
              termsLayer.push({ width: width, occupied: false });
            }

            for (let i = 0; i < item.occupied.length; i++) {
              let width = calculateLength(
                item.occupied[i].begin,
                item.occupied[i].end
              );
              termsLayer.push({ width: width, occupied: true });

              let emptyWidth = calculateLength(
                item.occupied[i].end,
                i + 1 != item.occupied.length
                  ? item.occupied[i + 1].begin
                  : "22:00"
              );
              termsLayer.push({ width: emptyWidth, occupied: false });
            }

            self.classrooms.push({
              label: item.number,
              type: item.type,
              id: item.id,
              capacity: item.capacity,
              termsLayer: termsLayer
            });
          }
        });
    });
  }
}
</script>

<template>
  <div>
    <h3>Filtruj sale</h3>
    <ClassroomField
      v-for="item in this.classrooms"
      :key="item.id"
      :label="item.label"
      :capacity="item.capacity"
      :id="item.id"
      :type="item.type"
      :termsLayer="item.termsLayer"
      :reservation="reservationLayer"
    />
  </div>
</template>