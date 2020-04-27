<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import ClassroomField from "./ClassroomField.vue";

@Component({
  components: {
    ClassroomField
  }
})
export default class ClassroomPicker extends Vue {}
</script>

<template>
  <div>
    <h3>Filtruj sale</h3>
    <ClassroomField
      label="Sala 4"
      :capacity="40"
      type="Sala ćwiczeniowa"
      :terms="[{startTime: '10:00', endTime: '12:00'}, {startTime: '14:00', endTime: '15:30'},
      {startTime: '16:00', endTime: '17:45'}]"
      :reservation="{startTime: '15:00', endTime: '19:00'}"
    />
    <ClassroomField
      label="Sala 4"
      :capacity="40"
      type="Sala ćwiczeniowa"
      :terms="[{startTime: '08:00', endTime: '11:45'}, {startTime: '13:30', endTime: '16:00'}]"
      :reservation="{startTime: '15:00', endTime: '19:00'}"
    />
  </div>
</template>