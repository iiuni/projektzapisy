<script setup lang="ts">
// Main Vue component for Timetable Prototype.
//
// The component has two direct children. One is responsible for displaying the
// list of available courses and selecting ones to present on the timemtable.
// The other one is the timetable itself. The set of currently displayed groups
// is maintained by the Vuex store (`../store/index.ts`).
// import { mixin as VueTimers } from "vue-timers";

// TODO Rename it to PrototypeTimetable
import SimpleTimetable from "./SimpleTimetable.vue";
import { computed, provide } from "vue";
import { useStore } from "vuex";

// Will be injected in Day.vue
provide("isPrototype", true);

const store = useStore();
const groupsGetter = computed(() => store.getters["groups/visibleGroups"]);
// TODO2 whats up with this timer?
// mixins: [VueTimers],
//   timers: {
//     update: {
//       time: 60 * 1000, // run every minute
//       autostart: true,
//       repeat: true,
//       isSwitchTab: true, // deactivate when tab is inactive.
//     },
//   },
// })
// this.$store.dispatch("groups/queryUpdatedGroupsStatus");
store.dispatch("groups/initFromJSONTag");
store.dispatch("courses/initFromJSONTag");
</script>

<template>
  <div class="col">
    <SimpleTimetable :groups="groupsGetter" />
  </div>
</template>
