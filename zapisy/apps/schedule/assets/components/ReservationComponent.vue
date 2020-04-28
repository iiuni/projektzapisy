<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import ClassroomPicker from "./ClassroomPicker.vue";

@Component({
  components: {
    ClassroomPicker
  }
})
export default class ReservationComponent extends Vue {}
</script>

<template>
  <div>
    <nav>
      <div class="nav nav-tabs" id="nav-tab" role="tablist">
        <a
          class="nav-item nav-link active"
          id="nav-place-in-tab"
          data-toggle="tab"
          href="#nav-place-in"
          role="tab"
          aria-controls="nav-place-in"
          aria-selected="false"
        >Sala Instytutu</a>
        <a
          class="nav-item nav-link"
          id="nav-place-out-tab"
          data-toggle="tab"
          href="#nav-place-out"
          role="tab"
          aria-controls="nav-place-out"
          aria-selected="true"
        >Miejsce zewnętrzne</a>
      </div>
    </nav>

    <div class="tab-content mt-3" id="nav-tabContent">
      <div
        class="tab-pane fade show active"
        id="nav-place-in"
        role="tabpanel"
        aria-labelledby="nav-place-in-tab"
      >
        <ClassroomPicker />
      </div>
      <div
        class="tab-pane fade"
        id="nav-place-out"
        role="tabpanel"
        aria-labelledby="nav-place-out-tab"
      >pupa</div>
    </div>
  </div>
</template>