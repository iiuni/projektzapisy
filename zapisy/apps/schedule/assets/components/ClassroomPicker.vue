<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import axios from "axios";
import { TermDisplay, Classroom, isFree, calculateLength } from "../terms";
import ClassroomField from "./ClassroomField.vue";

type ReservationTerm ={
  day: string;
  start: string;
  end: string;
  roomId: number | null;
  place: string;
  deleted?: boolean;
};

type OccupiedInterval = {
  begin: string;
  end: string;
};

type ClassroomApiItem = {
  id: number;
  number: string;
  type: string;
  capacity: number;
  occupied: OccupiedInterval[];
};

const ClassroomPickerDefinition = Vue.extend({
  components: {
    ClassroomField,
  },
  props: {
    activeTerm: {
      type: Object as () => ReservationTerm | null,
      default: null,
    },
    terms: {
      type: Array as () => ReservationTerm[],
      default() {
        return [];
      },
    },
    activeTermIndex: {
      type: Number,
      default: -1,
    },
  },
  data: () => {
    return {
      showOccupied: false,
    };
  },
  watch: {
    activeTerm: {
      handler: "onActiveTermChanged",
      immediate: true,
      deep: true,
    },
  },
});

@Component
export default class ClassroomPicker extends ClassroomPickerDefinition {
  activeTerm!: ReservationTerm | null;
  terms!: ReservationTerm[];
  activeTermIndex!: number;
  showOccupied!: boolean;

  classrooms: Classroom[] = [];
  unoccupiedClassrooms: Classroom[] = [];
  reservationLayer: TermDisplay[] = [];

  get displayedClassrooms(): Classroom[] {
    return this.showOccupied ? this.classrooms : this.unoccupiedClassrooms;
  }

  clearState() {
    this.classrooms = [];
    this.unoccupiedClassrooms = [];
    this.reservationLayer = [];
  }

  getLocalOccupiedForRoom(roomId: number, day: string): OccupiedInterval[] {
    return this.terms
      .filter((term, index) => {
        return (
          index !== this.activeTermIndex &&
          !term.deleted &&
          term.roomId === roomId &&
          term.day === day &&
          Boolean(term.start) &&
          Boolean(term.end)
        );
      })
      .map((term) => ({
        begin: term.start,
        end: term.end,
      }));
  }

  mergeOccupied(occupied: OccupiedInterval[]): OccupiedInterval[] {
    const sortedOccupied = [...occupied].sort((left, right) =>
      left.begin.localeCompare(right.begin)
    );
    const mergedOccupied: OccupiedInterval[] = [];

    for (const term of sortedOccupied) {
      if (
        mergedOccupied.length > 0 &&
        term.begin <= mergedOccupied[mergedOccupied.length - 1].end
      ) {
        mergedOccupied[mergedOccupied.length - 1].end =
          term.end > mergedOccupied[mergedOccupied.length - 1].end
            ? term.end
            : mergedOccupied[mergedOccupied.length - 1].end;
        continue;
      }

      mergedOccupied.push({ ...term });
    }

    return mergedOccupied;
  }

  onActiveTermChanged() {
    this.refreshClassrooms();
  }

  updateUnoccupiedClassrooms(begin: string, end: string) {
    this.unoccupiedClassrooms = this.classrooms.filter((item) => {
      return isFree(item.rawOccupied, begin, end);
    });
  }

  refreshReservationLayer() {
    if (!this.activeTerm) {
      this.reservationLayer = [];
      return;
    }

    let start = this.activeTerm.start;
    let end = this.activeTerm.end;

    if (!start || !end || start > end || end < "08:00" || start > "22:00") {
      this.reservationLayer = [];
      this.unoccupiedClassrooms = [...this.classrooms];
      return;
    }

    if (start < "08:00") {
      start = "08:00";
    }
    if (end > "22:00") {
      end = "22:00";
    }

    this.updateUnoccupiedClassrooms(start, end);

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

  refreshClassrooms() {
    if (!this.activeTerm) {
      this.clearState();
      return;
    }

    const date = this.activeTerm.day;

    if (date === "") {
      this.clearState();
      return;
    }

    const encodedDate = encodeURIComponent(date);

    axios.get<Record<string, ClassroomApiItem>>("/classrooms/get_terms/" + encodedDate + "/").then((response) => {
      this.classrooms = [];
      for (const item of Object.values(response.data)) {
        const termsLayer: TermDisplay[] = [];
        const mergedOccupied = this.mergeOccupied([
          ...item.occupied,
          ...this.getLocalOccupiedForRoom(item.id, date),
        ]);

        let lastFree = "08:00";

        for (const occ of mergedOccupied) {
          const emptyWidth = calculateLength(lastFree, occ.begin);
          termsLayer.push({
            width: emptyWidth,
            occupied: false,
          });

          const width = calculateLength(occ.begin, occ.end);
          termsLayer.push({
            width: width,
            occupied: true,
          });
          lastFree = occ.end;
        }

        if (lastFree < "22:00") {
          termsLayer.push({
            width: calculateLength(lastFree, "22:00"),
            occupied: false,
          });
        }

        this.classrooms.push({
          label: item.number,
          type: item.type,
          id: item.id,
          capacity: item.capacity,
          termsLayer: termsLayer,
          rawOccupied: mergedOccupied,
        });
      }
      this.refreshReservationLayer();
    });
  }

  onSelectRoom(payload: { roomId: number; label: string }) {
    this.$emit("select-room", payload);
  }
}
</script>

<template>
  <div>
    <h3>Filtruj sale</h3>
    <div class="form-check mb-3">
        <input
          type="checkbox"
          class="form-check-input"
          id="showOccupied"
          v-model="showOccupied"
        />
        <label class="form-check-label" for="showOccupied"
          >Pokaż zajęte</label
        >
    </div>
    <ClassroomField
      v-for="item in displayedClassrooms"
      :key="item.id"
      :label="item.label"
      :capacity="item.capacity"
      :id="item.id"
      :type="item.type"
      :termsLayer="item.termsLayer"
      :reservationLayer="reservationLayer"
      @select-room="onSelectRoom"
    />
  </div>
</template>
