<script lang="ts">
// Main Vue component for Timetable Prototype.
//
// The component has two direct children. One is responsible for displaying the
// list of available courses and selecting ones to present on the timemtable.
// The other one is the timetable itself. The set of currently displayed groups
// is maintained by the Vuex store (`../store/index.ts`).
import { values } from "lodash";
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";
import VueTimers from "vue-timers/mixin";

import { Group, GroupJSON } from "../models";
import CourseList, { CourseObject } from "./CourseList.vue";
import PrototypeTimetable from "./PrototypeTimetable.vue";

@Component({
  components: {
    CourseList,
    PrototypeTimetable
  },
  computed: {
    ...mapGetters("courses", {
      courses: "courses"
    }),
    ...mapGetters("groups", {
      groupsGetter: "visibleGroups"
    })
  },
  mixins: [VueTimers],
  timers: {
    update: { 
      time: 60*1000,  // run every minute
      autostart: true,
      repeat: true,
      isSwitchTab: true,  // deactivate when tab is inactive.
    }
  },
})
export default class Prototype extends Vue {
  created() {
    this.$store.dispatch("groups/initFromJSONTag");
    this.$store.dispatch("courses/initFromJSONTag");
  }

  update() {
    this.$store.dispatch("groups/queryUpdatedGroupsStatus");
  }
}
</script>

<template>
    <div class="col">
        <PrototypeTimetable :groups="groupsGetter"/>
    </div>
</template>
