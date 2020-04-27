<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import $ from "jquery";
import axios from "axios";
import ClassroomField from "./ClassroomField.vue";

@Component({
  components: {
    ClassroomField
  }
})
export default class ClassroomPicker extends Vue {
  reservationPreview: { width: string; occupied: boolean }[] = [];
  calculateLength = (startTime: string, endTime: string) => {
    let hS = Number(startTime.substr(0, 2));
    let mS = Number(startTime.substr(3, 5));
    let hE = Number(endTime.substr(0, 2));
    let mE = Number(endTime.substr(3, 5));

    let hD = hE - hS;
    let mD = mE - mS < 0 ? 60 + mE - mS : mE - mS;
    hD = mE - mS < 0 ? hD - 1 : hD;

    return String(((hD + mD / 60) / 14) * 100) + "%";
  };

  mounted() {
    let self = this;
    $(".form-time").change(function(event) {
      let start = $("#start-time").val();
      let end = $("#end-time").val();

      self.reservationPreview = [];
      self.reservationPreview.push({
        width: self.calculateLength("08:00", start),
        occupied: false
      });
      self.reservationPreview.push({
        width: self.calculateLength(start, end),
        occupied: true
      });
      self.reservationPreview.push({
        width: self.calculateLength(end, "22:00"),
        occupied: false
      });
    });

    $(".form-date").change(function(event) {
      var date = $(".form-date")
        .val()
        .split("-");

      axios
        .get(
          "/classrooms/terms/" + +date[0] + "/" + date[1] + "/" + date[2] + "/"
        )
        .then(response => {
          console.log(response);
        });
    });
  }
}
</script>

<template>
  <div>
    <h3>Filtruj sale</h3>
    <ClassroomField
      label="Sala 4"
      :capacity="40"
      :id="11"
      type="Sala ćwiczeniowa"
      :terms="[{startTime: '10:00', endTime: '12:00'}, {startTime: '14:00', endTime: '15:30'},
      {startTime: '16:00', endTime: '17:45'}]"
      :reservation="reservationPreview"
    />
    <ClassroomField
      label="Sala 4"
      :capacity="40"
      :id="10"
      type="Sala ćwiczeniowa"
      :terms="[{startTime: '08:00', endTime: '11:45'}, {startTime: '13:30', endTime: '16:00'}]"
      :reservation="reservationPreview"
    />
  </div>
</template>