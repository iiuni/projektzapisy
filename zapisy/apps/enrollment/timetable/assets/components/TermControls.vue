<script lang="ts">
// This component presents a single group term in a week. It extends upon
// TermComponent by adding control buttons that allow to enqueue/dequeue to
// the group and to pin it.
import Component from "vue-class-component";
import Vue from "vue";
import TermComponent from "./Term.vue";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { faCarSide } from "@fortawesome/free-solid-svg-icons/faCarSide";

import { Term, Group } from "../models";

const TermControlsProps = Vue.extend({
  props: {
    term: Term,
  },
});

@Component({
  components: {
    Term: TermComponent,
    FontAwesomeIcon,
  },
})
export default class TermControlsComponent extends TermControlsProps {
  controlsVisible: boolean = false;
  faCarSide = faCarSide;

  get group(): Group {
    return this.term.group;
  }

  // Determines if a new enrollment record can be created into the group.
  get canEnqueue(): boolean {
    if (this.term.group.isEnrolled) return false;
    if (this.term.group.isEnqueued) return false;
    return this.term.group.canEnqueue;
  }

  // Determines if an enrollment record exists and can be removed.
  get canDequeue(): boolean {
    if (!this.term.group.canDequeue) return false;
    if (this.term.group.isEnrolled) return true;
    if (this.term.group.isEnqueued) return true;
    return false;
  }

  pin() {
    this.$store.dispatch("groups/pin", this.term.group);
  }

  unpin() {
    this.$store.dispatch("groups/unpin", this.term.group);
  }

  enqueue() {
    const confirmMessage = [
      "Czy na pewno chcesz stanąć w kolejce do tej grupy?\n\n",
      "Gdy tylko w grupie będzie wolne miejsce (być może natychmiast), ",
      "zostanie dokonana próba wciągnięcia do niej studentów z kolejki. Jeśli ",
      "w momencie wciągania do grupy student nie spełnia warunków zapisu ",
      "(np. przekracza limit ECTS), jego rekord zostaje usunięty.",
    ].join("");

    if (confirm(confirmMessage)) {
      this.$store.dispatch("groups/enqueue", this.term.group);
    }
  }

  dequeue() {
    const confirmMessage = "Czy na pewno chcesz opuścić tę grupę/kolejkę?";
    if (confirm(confirmMessage)) {
      this.$store.dispatch("groups/dequeue", this.term.group);
    }
  }
}
</script>

<template>
  <Term
    :term="term"
    @mouseover.native="controlsVisible = true"
    @mouseout.native="controlsVisible = false"
  >
    <transition name="fade">
      <div class="controls" v-if="controlsVisible">
        <span
          v-if="group.isPinned"
          class="unpin"
          title="Odepnij grupę od planu."
          @click="unpin()"
        ></span>
        <span
          v-else
          class="pin"
          title="Przypnij grupę do planu."
          @click="pin()"
        ></span>

        <span
          v-if="canEnqueue"
          class="enqueue"
          title="Zapisz do grupy/kolejki."
          @click="enqueue()"
        ></span>
        <span
          v-if="canDequeue"
          class="dequeue"
          title="Wypisz z grupy/kolejki."
          @click="dequeue()"
        ></span>
        <span
          v-if="term.group.autoEnrollment"
          class="auto-enrollment"
          title="Grupa z auto-zapisem."
        >
          <font-awesome-icon icon="car-side" transform="shrink-3 left-2" />
        </span>
      </div>
    </transition>
  </Term>
</template>

<style lang="scss" scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.controls {
  position: absolute;
  background: white;
  top: 0;
  left: 0;
  cursor: default;
  width: auto;
  border: 1px solid #666666;
  border-top: 0;
  border-left: 0;
  border-radius: 4px 0;
  box-shadow: 0 0 3px rgba(0, 0, 0, 0.5);
  z-index: 30;
}

.controls span {
  display: block;
  width: 12px;
  height: 12px;
  margin: 3px;
  overflow: hidden;
  cursor: pointer;
}
</style>

<style lang="scss">
span.pin {
  background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAQAAAD8fJRsAAAAi0lEQVQY032PMQoCUQxEg4iCdgoK2qlvDmLhWfYydl5AbLyXIh9stnKxSSw+f11FTCAE3gzDmP0f9SVNfwA2aji3sqFmbxCq2asicdWDKJoVoY81DRiz1JYg5HJCnkHiTsMT/3KYmbFoHSHPXwlfKxQE+bpKOCiU2DHhwJELtwLmOlF1eo263Xvdyi8RHEhw4FPwSQAAAABJRU5ErkJggg==);
}

span.unpin {
  background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAQAAAD8fJRsAAAAsUlEQVQY02NgQAKqpar/VXwZ0IGKh+p/MMxGFZZVeab6DwTVfqshpFQ5VLer/lf7D5T4rwbEqr4MqlwqhcouauWqEEGgMAiq/mdQCQQKfVb9pQYVhChQaWZQZlddpwbR/g8s+V/1jVos2Hx1NrW1UCGQ9Ck1FYSLWsHO/Kf6V7VLhQ8h7KD6QWWaKlCX6lcVH7iwspLKTuUABgYlNtUtQOPqET6YpqIHYalxqEar8sPEAdj8UUYH1HpBAAAAAElFTkSuQmCC);
}

span.enqueue {
  background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAQAAAD8fJRsAAAAoklEQVQY02XQLw6DMBiH4Q+FKeESS0UPMA+uYqS4Db+r9CrIZWZD04wjVMBI3c9PtWZjkn953SNfAq1KbHVx5o1iiRGYy29GhGMw/ZJTq2SrfT2JcHZLLmXHA5+0v7e22jEP0ow5kj13VoGBCARm1YJLpIhAhHjMpNkyiHB4NtpvGUTdSQz1T3vZWjUziPTAP6J/NC4DmxlE168eXgUOiNdz/lSxl2uEe8+QAAAAAElFTkSuQmCC);
}

span.dequeue {
  background-image: url(data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAYAAABWdVznAAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAC4jAAAuIwF4pT92AAAAB3RJTUUH4ggOEhs2PtkFxgAAABl0RVh0Q29tbWVudABDcmVhdGVkIHdpdGggR0lNUFeBDhcAAAE5SURBVCjPfZCxSlxhEIW/M/Pf+7uSXddFcEkTSBXClmks7ISgpLBIKSwoAYsEwSLkPdJISJmUpgo+QbBIIalELANuG1ACbvTeSeEim0v0lMOcM+cbACEt49oFetwjd9zBHGyN0AbSQ7ATiPP/7A8knju4QC0sCfkqUT8pLUZVMALAmMXyOlFvRehoYu4WUCyitInSN+FfMZag3QHbQX6A0gqAmjWhHKB4d8MTv7DoQvpANf5yD14aoPwDpUNUvmkkNvRgdp4r3kPVIVSjeIYYQZzeIE1L1uf39UeoH6PYAxuCHYO/xHO/0b7s4nkPyz9R8fZ2PjM/h4rPeH5Fe2HCnHG8tY21zlCxD7nzT5iVT5Hvg/oJgDE9uHoBdgl8QtUFMWWo/xyDf8fj0eRCO6M0BL0G2nd8LpGwv420RBxssgl5AAAAAElFTkSuQmCC);
}
span.auto-enrollment {
  font-size: 12px;
}
</style>
