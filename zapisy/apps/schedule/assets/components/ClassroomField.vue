<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import $ from "jquery";
import { TermDisplay } from "../terms";

const ClassroomFieldProps = Vue.extend({
  props: {
    label: String,
    type: String,
    capacity: Number,
    id: Number,
    termsLayer: {
      type: Array as () => Array<TermDisplay>,
      default() {
        return [];
      },
    },
    reservationLayer: {
      type: Array as () => Array<TermDisplay>,
      default() {
        return [];
      },
    },
  },
});

@Component
export default class ClassroomField extends ClassroomFieldProps {
  // When changing location using widget we have to change values of room and place
  // fields of currently edited term. We do it using JQuery.
  onClick() {
    $(".active-term").find(".form-room").val(this.id);
    $(".active-term")
      .find(".form-place")
      .val("Sala " + this.label);
    $([document.documentElement, document.body]).animate(
      {
        scrollTop: $("#term-forms").offset()!.top,
      },
      500
    );
  }
}
</script>

<template>
  <div class="p-3 text-center">
    <p class="font-weight-bold">Sala numer {{ label }}</p>
    <div class="container p-0 m-0">
      <div class="row">
        <div class="col-sm-2 p-1">
          <button type="button" class="btn btn-primary" v-on:click="onClick">
            Wybierz
          </button>
        </div>
        <div class="col-sm-8 p-1">
          <div class="container p-0 m-0">
            <div class="row">
              <div class="col">
                <div style="height: 35px">
                  <div class="progress bg-light" style="height: 35px">
                    <div
                      role="progressbar"
                      v-for="(item, key) in termsLayer"
                      :key="key"
                      :class="
                        'progress-bar ' +
                        (item.occupied
                          ? 'bg-secondary progress-bar-striped'
                          : 'bg-transparent')
                      "
                      :style="'width: ' + item.width"
                    >
                      {{ item.occupied ? "Zajęte" : "" }}
                    </div>
                  </div>
                  <div
                    style="
                      z-index: 2;
                      position: relative;
                      top: -35px;
                      opacity: 0.5;
                      width: 100%;
                    "
                  >
                    <div class="progress bg-transparent" style="height: 35px">
                      <div
                        role="progressbar"
                        v-for="(item, key) in reservationLayer"
                        :key="key"
                        :class="
                          'progress-bar ' +
                          (item.occupied ? 'bg-primary' : 'bg-transparent')
                        "
                        :style="'width: ' + item.width"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="row" style="font-family: monospace; position: relative">
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
          </div>
        </div>
        <div class="col-sm-2 p-1">{{ type }}, pojemność: {{ capacity }}</div>
      </div>
    </div>
  </div>
</template>
