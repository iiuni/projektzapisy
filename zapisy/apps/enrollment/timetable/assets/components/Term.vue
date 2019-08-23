<script lang="ts">
// Term component is responsible for displaying a singe course term on the
// timetable.
//
// The term is positioned vertically on the CSS grid according to the starting
// and ending hours. When clicked, a large popup will be presented with all the
// group information.
import Component from "vue-class-component";
import Vue from "vue";
import { Group, Term, Hour, Minute, TimeTuple, nameDay } from "../models";

// This is a way to make TypeScript recognise the props and their types.
const TermProps = Vue.extend({
  props: {
    term: Term
  }
});

@Component
export default class TermComponent extends TermProps {
  get group(): Group {
    return this.term.group;
  }

  get title(): string {
    switch (this.boxClass) {
      case "enrolled":
        return "Jesteś zapisany do tej grupy.";
      case "enqueued":
        return "Jesteś w kolejce do tej grupy";
      case "pinned":
        return "Ta grupa jest przypięta do twojego planu";
      default:
        return "";
    }
  }

  popupVisible: boolean = false;
  // Pops out course information. The event is there because mouseout does not
  // work on touch devices like phones.
  showPopup() {
    this.popupVisible = true;
    window.addEventListener("touchend", this.hidePopup);
  }

  hidePopup() {
    this.popupVisible = false;
    window.removeEventListener("touchend", this.hidePopup);
  }

  weekday = nameDay(this.term.weekday);

  // The rows spanned by the box. They represent starting and ending time of the
  // group term.
  get boxStyle() {
    const startRow: number = this.timeTupleToRow(this.term.startTime);
    const endRow: number = this.timeTupleToRow(this.term.endTime);
    return {
      gridRow: `${startRow} / ${endRow}`
    };
  }

  // boxClass determines the color of the box based on the group's status.
  get boxClass(): string {
    if (this.term.group.isEnrolled) return "enrolled";
    if (this.term.group.isEnqueued) return "enqueued";
    if (this.term.group.isPinned) return "pinned";
    return "";
  }

  // Returns a short name of the course if available. Otherwise sticks with a
  // regular name.
  get courseShortName(): string {
    if (this.term.group.course.shortName) {
      return this.term.group.course.shortName;
    }
    return this.term.group.course.name;
  }

  // Transforms a TimeTouple into css grid row number. It assumes that there is
  // a css grid row representing every 15 minutes starting with 8:00AM.
  timeTupleToRow([h, m]: TimeTuple): number {
    const hourRow = (h - 8) * 4 + 1;
    const minuteRow = Math.floor(m / 15);
    return hourRow + minuteRow;
  }
}
</script>

<template>
<div
    class="term-box"
    :style="boxStyle"
    :class="boxClass">
  <div class="term-info" :title="title" @click="showPopup()">
    <span class="short-name">{{ courseShortName }}</span>
    <span class="teacher">{{ group.teacher.name }}</span>
    <span class="classrooms">s. {{ term.classrooms }}</span>
    <span class="group-type">{{ group.type }}</span>
  </div>

  <transition name="fade">
    <div v-if="popupVisible" class="popup" @mouseleave="hidePopup()">
        <span class="popup-name">
          <a :href="group.course.url">{{ group.course.name }}</a>
        </span>
        <p class="popup-info">
            {{ group.type }}
            ({{ weekday.toLocaleLowerCase() }} {{ term.startTimeString }}-{{ term.endTimeString }})
        </p>
        <p class="popup-info">
          Prowadzący:
          <a :href="group.teacher.url">{{ group.teacher.name }}</a>
        </p>
        <p class="popup-info">Sala: {{ term.classrooms }}</p>
        <a class="group-link" :href="group.url">
          lista studentów zapisanych do grupy
          ({{ group.numEnrolled }}/{{ group.limit }}<span v-for="gs of group.guaranteedSpots" :key="gs.role" title="">+{{ gs.limit }}</span>)
        </a>
    </div>
  </transition>

  <slot></slot>

</div>
</template>

<style lang="scss">
.term-box {
  position: relative;
  border: 1px solid #666666;
  background: #f8f8f8;
  border-radius: 4px;
  color: black;
  line-height: 120%;
}

.term-info {
  overflow: hidden;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}

.term-box.enrolled,
.term-box.enrolled .classrooms,
.term-box.enrolled .group-type {
  background: #e0eeee;
}

.term-box.enqueued,
.term-box.enqueued .classrooms,
.term-box.enqueued .group-type {
  background: #f5e5c4;
}

.term-box.pinned,
.term-box.pinned .classrooms,
.term-box.pinned .group-type {
  background: #fae8f8;
}

.short-name {
  display: block;
  padding: 2px;
  padding-bottom: 0;
  max-height: 2rem;
  overflow: hidden;

  font-size: 14px;
}

.teacher {
  display: block;
  padding: 2px;
  padding-top: 0;
  white-space: nowrap;
  overflow: hidden;

  font-size: 10px;
}

.classrooms {
  position: absolute;
  bottom: 0;
  right: 1px;
  padding: 1px 2px;

  font-size: 10px;
  text-align: right;
  white-space: nowrap;
  z-index: 2;
  overflow: hidden;

  background: #f8f8f8;
  border-radius: 3px;
}

.group-type {
  position: absolute;
  display: block;
  bottom: 0;
  left: 0;
  padding: 1px 2px;
  padding-top: 0;
  line-height: 100%;
  overflow: hidden;

  font-size: 10px;
  color: #666666;
  z-index: 1;
  background: #f8f8f8;

  border-radius: 3px;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 1s;
}
.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.popup {
  position: absolute;
  top: -25px;
  left: -25px;
  width: 300px;
  padding: 10px;
  z-index: 50;
  border: 1px solid #666666;
  border-radius: 4px;
  background: #f8f8f8;
  overflow: hidden;
  box-shadow: 2px 2px 3px rgba(0, 0, 0, 0.15);
}

.popup-name {
  display: block;
  font-size: 1.2rem;
  padding-bottom: 10px;
}

.popup-info {
  display: block;
  margin: 0;
  padding: 0 1px;
}
</style>
