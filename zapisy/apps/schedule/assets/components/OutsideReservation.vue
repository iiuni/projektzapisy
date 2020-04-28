<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import ClassroomPicker from "./ClassroomPicker.vue";

@Component({})
export default class OutsideReservation extends Vue {}
</script>

<template>
  <div>
    <div class="alert alert-warning alert-dismissible fade show" role="alert">
      Musisz samemu zatroszczyć się o rezerwację!
      <button
        type="button"
        class="close"
        data-dismiss="alert"
        aria-label="Close"
      >
        <span aria-hidden="true">&times;</span>
      </button>
    </div>
    <div id="inputplacediv" class="container">
      <div class="form-group row">
        <label for="inputplace" class="col-sm-2 col-form-label">Miejsce</label>
        <div class="col-sm-10 input-group">
          <input
            type="text"
            class="form-control"
            id="inputplace"
            placeholder="np. Instytu Matematyczny, Sala HS"
          />
          <div class="input-group-append">
            <button type="button" class="btn btn-info" id="addoutsidelocation">Wybierz</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>