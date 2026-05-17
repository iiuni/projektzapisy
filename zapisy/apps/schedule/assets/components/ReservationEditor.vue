<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import ClassroomPicker from "./ClassroomPicker.vue";
import dayjs from "dayjs";
import duration from "dayjs/plugin/duration";

dayjs.extend(duration);

export type Term = {
  id: number | null;
  day: string;
  start: string;
  end: string;
  roomId: number | null;
  place: string;
  deleted: boolean;
};

type EditableTermField = "day" | "start" | "end" | "place";
type LocationTab = "inside" | "outside";

function createEmptyTerm(): Term {
  const timeStampFrom = dayjs();
  const timeStampTo = timeStampFrom.add(dayjs.duration({ minutes: 30 }));

  // Pre-fill a short slot only when it stays within one calendar day; otherwise
  // leave the date/time empty and let the user choose a valid reservation window.
  const day =
    timeStampFrom.date() === timeStampTo.date()
      ? timeStampFrom.format("YYYY-MM-DD")
      : "";
  const start = day ? timeStampFrom.format("HH:mm") : "";
  const end = day ? timeStampTo.format("HH:mm") : "";

  return {
    id: null,
    day,
    start,
    end,
    roomId: null,
    place: "",
    deleted: false,
  };
}

@Component({
  components: {
    ClassroomPicker,
  },
  props: {
    initialTerms: {
      type: Array as () => Term[],
      default() {
        return [];
      },
    },
    initialFormsCount: {
      type: Number,
      default: 0,
    },
    minNumForms: {
      type: Number,
      default: 1,
    },
    maxNumForms: {
      type: Number,
      default: 1000,
    },
  },
})
export default class ReservationEditor extends Vue {
  initialTerms!: Term[];
  initialFormsCount!: number;
  minNumForms!: number;
  maxNumForms!: number;

  terms: Term[] = [];
  activeTermIndex = 0;
  activeLocationTab: LocationTab = "inside";
  outsidePlaceInput = "";

  created(): void {
    const initialTerms = this.initialTerms.map((term: Term) => ({ ...term }));
    // We work on a local copy so the editor can freely mutate rows before the
    // final HTML form submit sends everything back to Django.
    this.terms = initialTerms.length > 0 ? initialTerms : [createEmptyTerm()];
    this.ensureValidActiveTerm();
    this.syncLocationTabWithActiveTerm();
  }

  get visibleTermEntries(): Array<{ term: Term; index: number }> {
    return this.terms
      .map((term: Term, index: number) => ({ term, index }))
      .filter(({ term }) => !term.deleted);
  }

  get activeTerm(): Term | null {
    const term = this.terms[this.activeTermIndex];
    if (!term || term.deleted) {
      return null;
    }
    return term;
  }

  addTerm(): void {
    const base = this.activeTerm;
    // "Add term" copies the currently edited date/time to speed up entering a
    // series of reservations, but it intentionally clears the location so each
    // new row must choose a room/place on its own.
    const newTerm: Term = base
      ? {
          id: null,
          day: base.day,
          start: base.start,
          end: base.end,
          roomId: null,
          place: "",
          deleted: false,
        }
      : createEmptyTerm();
    this.terms.push(newTerm);

    this.activeTermIndex = this.terms.length - 1;
    this.syncLocationTabWithActiveTerm();
  }

  setActiveTerm(index: number): void {
    if (index < 0 || index >= this.terms.length) {
      return;
    }

    if (this.terms[index].deleted) {
      return;
    }

    this.activeTermIndex = index;
    this.syncLocationTabWithActiveTerm();
  }

  updateTermField(index: number, field: EditableTermField, event: Event): void {
    const target = event.target as HTMLInputElement | null;
    if (!target) {
      return;
    }

    if (index < 0 || index >= this.terms.length) {
      return;
    }

    // Vue updates the visible editor state first; hidden inputs are derived from
    // `terms` in the template, so the Django formset receives the same values on submit.
    this.$set(this.terms[index], field, target.value);
  }

  selectRoomForActiveTerm(roomId: number, label: string): void {
    if (!this.activeTerm) {
      return;
    }

    // Picking an internal classroom writes both the foreign key used by Django
    // and the human-readable label shown in the read-only location column.
    this.activeTerm.roomId = roomId;
    this.activeTerm.place = `Sala ${label}`;
    this.activeLocationTab = "inside";
  }

  setOutsidePlace(place: string): void {
    if (!this.activeTerm) {
      return;
    }

    // External locations are represented only by free text, so we clear `roomId`
    // to make the submitted row unambiguously different from a classroom booking.
    this.activeTerm.roomId = null;
    this.activeTerm.place = place;
    this.outsidePlaceInput = place;
    this.activeLocationTab = "outside";
  }

  removeTerm(index: number): void {
    if (index < 0 || index >= this.terms.length) {
      return;
    }

    const term = this.terms[index];

    if (term.id !== null) {
      // To znaczy, że edytujemy istniejący termin, więc go nie usuwamy, tylko oznaczamy jako usunięty,
      // żeby formularz Django mógł go poprawnie obsłużyć
      term.deleted = true;
    } else {
      this.terms.splice(index, 1);
    }

    this.ensureValidActiveTerm();
  }

  ensureValidActiveTerm(): void {
    if (this.activeTerm && !this.activeTerm.deleted) {
      return;
    }

    // Django formsets still expect at least one row, so after deletions we always
    // move focus to the next visible term and recreate an empty one if needed.
    const firstVisibleIndex = this.terms.findIndex(
      (term: Term) => !term.deleted
    );
    this.activeTermIndex = firstVisibleIndex === -1 ? 0 : firstVisibleIndex;

    if (firstVisibleIndex === -1) {
      this.terms.push(createEmptyTerm());
      this.activeTermIndex = this.terms.length - 1;
    }

    this.syncLocationTabWithActiveTerm();
  }

  setLocationTab(tab: LocationTab): void {
    this.activeLocationTab = tab;
    if (tab === "outside" && this.activeTerm) {
      this.outsidePlaceInput =
        this.activeTerm.roomId === null ? this.activeTerm.place : "";
    }
  }

  applyOutsidePlace(): void {
    this.setOutsidePlace(this.outsidePlaceInput);
  }

  syncLocationTabWithActiveTerm(): void {
    if (!this.activeTerm) {
      this.activeLocationTab = "inside";
      this.outsidePlaceInput = "";
      return;
    }

    // The tab selection is derived from the serialized term fields so reopening
    // or switching rows preserves whether the place comes from a classroom pick
    // or a free-text external location.
    if (this.activeTerm.roomId === null && this.activeTerm.place) {
      this.activeLocationTab = "outside";
      this.outsidePlaceInput = this.activeTerm.place;
      return;
    }

    this.activeLocationTab = "inside";
    this.outsidePlaceInput = "";
  }

  fieldName(index: number, field: string): string {
    // Names must exactly match Django formset conventions: term_set-<row>-<field>.
    return `term_set-${index}-${field}`;
  }

  serializeValue(value: string | number | null): string {
    return value === null ? "" : String(value);
  }

  getTermErrors(term: Term): string[] {
    const errors: string[] = [];
    if (term.deleted) return errors;

    if (!term.day) {
      errors.push("Wybierz dzień");
    }
    if (!term.start) {
      errors.push("Podaj godzinę rozpoczęcia");
    }
    if (!term.end) {
      errors.push("Podaj godzinę zakończenia");
    }
    if (term.start && term.end && term.start >= term.end) {
      errors.push("Godzina zakończenia musi być późniejsza niż rozpoczęcia");
    }
    if (!term.place) {
      errors.push("Wybierz lokalizację");
    }

    return errors;
  }
}
</script>

<template>
  <div>
    <input type="hidden" name="term_set-TOTAL_FORMS" :value="terms.length" />
    <input
      type="hidden"
      name="term_set-INITIAL_FORMS"
      :value="initialFormsCount"
    />
    <input type="hidden" name="term_set-MIN_NUM_FORMS" :value="minNumForms" />
    <input type="hidden" name="term_set-MAX_NUM_FORMS" :value="maxNumForms" />

    <div v-for="(term, index) in terms" :key="index" class="d-none">
      <input type="hidden" :name="fieldName(index, 'day')" :value="term.day" />
      <input
        type="hidden"
        :name="fieldName(index, 'start')"
        :value="term.start"
      />
      <input type="hidden" :name="fieldName(index, 'end')" :value="term.end" />
      <input
        type="hidden"
        :name="fieldName(index, 'place')"
        :value="term.place"
      />
      <input
        type="hidden"
        :name="fieldName(index, 'room')"
        :value="serializeValue(term.roomId)"
      />
      <input
        type="hidden"
        :name="fieldName(index, 'id')"
        :value="serializeValue(term.id)"
      />
      <input
        type="hidden"
        :name="fieldName(index, 'DELETE')"
        :value="term.deleted ? 'on' : ''"
      />
    </div>

    <div class="container">
      <div class="row font-weight-bold mb-2 border-bottom">
        <div class="col-3 col-lg-2 p-2 border">Dzień</div>
        <div class="col-2 p-2 border">Początek</div>
        <div class="col-2 p-2 border">Koniec</div>
        <div class="col-2 col-lg-3 p-2 border">Lokalizacja</div>
        <div class="col-3 p-2 border">Działania</div>
      </div>
    </div>

    <div class="mb-3">
      <div
        v-for="entry in visibleTermEntries"
        :key="entry.index"
        class="term-form"
        :class="entry.index === activeTermIndex ? 'active-term' : ''"
      >
        <div class="row p-2">
          <div class="col-3 col-lg-2 mb-0 px-1">
            <input
              type="date"
              class="form-control form-day"
              :disabled="entry.index !== activeTermIndex"
              :value="entry.term.day"
              @input="updateTermField(entry.index, 'day', $event)"
            />
          </div>

          <div class="col-2 mb-0 px-1">
            <input
              type="time"
              class="form-control form-time form-start"
              :disabled="entry.index !== activeTermIndex"
              :value="entry.term.start"
              @input="updateTermField(entry.index, 'start', $event)"
            />
          </div>

          <div class="col-2 mb-0 px-1">
            <input
              type="time"
              class="form-control form-time form-end"
              :disabled="entry.index !== activeTermIndex"
              :value="entry.term.end"
              @input="updateTermField(entry.index, 'end', $event)"
            />
          </div>

          <div class="col-2 col-lg-3 mb-0 px-1">
            <input
              type="text"
              readonly
              disabled
              class="form-control form-place m-0"
              :value="entry.term.place"
            />
          </div>

          <div class="col-3 mb-0">
            <button
              type="button"
              class="btn btn-primary edit-term-form mb-1"
              @click="setActiveTerm(entry.index)"
            >
              Edytuj
            </button>
            <button
              type="button"
              class="btn btn-danger delete-term-form mb-1"
              @click="removeTerm(entry.index)"
            >
              Usuń
            </button>
          </div>
        </div>
        <div v-if="getTermErrors(entry.term).length > 0" class="px-1 pb-2">
          <div
            class="text-danger fw-medium lh-sm"
            role="alert"
            aria-live="polite"
          >
            <div
              v-for="(error, eIdx) in getTermErrors(entry.term)"
              :key="eIdx"
              class="mb-1"
            >
              {{ error }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="d-flex gap-2 mb-3">
      <button type="button" class="btn btn-primary" @click="addTerm">
        Dodaj nowy termin
      </button>
    </div>

    <div>
      <nav>
        <div class="nav nav-tabs" role="tablist">
          <a
            href="#"
            class="nav-item nav-link"
            :class="activeLocationTab === 'inside' ? 'active' : ''"
            @click.prevent="setLocationTab('inside')"
            >Sala Instytutu</a
          >
          <a
            href="#"
            class="nav-item nav-link"
            :class="activeLocationTab === 'outside' ? 'active' : ''"
            @click.prevent="setLocationTab('outside')"
            >Miejsce zewnętrzne</a
          >
        </div>
      </nav>

      <div class="tab-content mt-3">
        <div
          v-show="activeLocationTab === 'inside'"
          class="tab-pane fade show active"
        >
          <ClassroomPicker
            v-if="activeTerm"
            :activeTerm="activeTerm"
            :terms="terms"
            :activeTermIndex="activeTermIndex"
            @select-room="selectRoomForActiveTerm($event.roomId, $event.label)"
          />
        </div>

        <div
          v-show="activeLocationTab === 'outside'"
          class="tab-pane fade show active"
        >
          <div
            class="alert alert-warning alert-dismissible fade show"
            role="alert"
          >
            Musisz samemu zatroszczyć się o rezerwację!
            <button
              type="button"
              class="btn-close"
              data-bs-dismiss="alert"
              aria-label="Close"
            ></button>
          </div>
          <div id="inputplacediv" class="container">
            <div class="form-group row">
              <label for="inputplace" class="col-sm-2 col-form-label"
                >Miejsce</label
              >
              <div class="col-sm-10 input-group">
                <input
                  id="inputplace"
                  type="text"
                  class="form-control"
                  placeholder="np. Instytut Matematyczny, Sala HS"
                  v-model="outsidePlaceInput"
                />
                <div class="input-group-append">
                  <button
                    type="button"
                    class="btn btn-info"
                    @click="applyOutsidePlace"
                  >
                    Wybierz
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
