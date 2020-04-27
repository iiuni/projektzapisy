<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { Term } from "../store/classrooms";

@Component({
  props: {
    label: String,
    type: String,
    capacity: Number,
    terms: {
      type: Array as () => Array<Term>,
      default: []
    },
    reservation: Object
  }
})
export default class ClassroomField extends Vue {
  visibleBlocks: { width: string; occupied: boolean }[] = [];
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
    if (this.terms.length != 0) {
      let width = this.calculateLength("08:00", this.terms[0].startTime);
      this.visibleBlocks.push({ width: width, occupied: false });
    }
    for (let i = 0; i < this.terms.length; i++) {
      let width = this.calculateLength(
        this.terms[i].startTime,
        this.terms[i].endTime
      );
      this.visibleBlocks.push({ width: width, occupied: true });

      let emptyWidth = this.calculateLength(
        this.terms[i].endTime,
        i + 1 != this.terms.length ? this.terms[i + 1].startTime : "22:00"
      );
      this.visibleBlocks.push({ width: emptyWidth, occupied: false });
    }

    this.reservationPreview.push({
      width: this.calculateLength("08:00", this.reservation.startTime),
      occupied: false
    });
    this.reservationPreview.push({
      width: this.calculateLength(
        this.reservation.startTime,
        this.reservation.endTime
      ),
      occupied: true
    });
    this.reservationPreview.push({
      width: this.calculateLength(this.reservation.endTime, "22:00"),
      occupied: false
    });
  }
}
</script>


<template>
  <div class="p-3 text-center">
    {{ label }}
    <div class="container p-0 m-0">
      <div class="row">
        <div class="col-sm-2 p-1">
          <button type="button" class="btn btn-primary">Wybierz</button>
        </div>
        <div class="col-sm-8 p-1">
          <div class="container p-0 m-0">
            <div class="row">
              <div class="col">
                <div style="height: 35px">
                  <div class="progress bg-light" style="height: 35px">
                    <div
                      role="progressbar"
                      v-for="(item, key) in visibleBlocks"
                      :key="key"
                      :class="'progress-bar ' + (item.occupied ? 'bg-secondary progress-bar-striped' : 'bg-transparent')"
                      :style="'width: ' + item.width"
                    >{{item.occupied ? 'Zajęte' : ''}}</div>
                  </div>
                  <div
                    style="z-index: 2; position: relative; top: -35px; opacity: 0.5; width: 100%"
                  >
                    <div class="progress bg-transparent" style="height: 35px">
                      <div
                        role="progressbar"
                        v-for="(item, key) in reservationPreview"
                        :key="key"
                        :class="'progress-bar ' + (item.occupied ? 'bg-primary' : 'bg-transparent')"
                        :style="'width: ' + item.width"
                      ></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div class="row" style="font-family:monospace; position: relative">
              <div class="d-flex flex-row justify-content-between" style="width: 100%">
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