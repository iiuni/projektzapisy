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
  }
})
export default class Prototype extends Vue {
  created() {
    this.$store.dispatch("groups/initFromJSONTag");
    this.$store.dispatch("courses/initFromJSONTag");
  }
}
</script>

<template>
<div class="row">
    <div class="span12 columns">
        <PrototypeTimetable :groups="groupsGetter"/>
    </div>
    <div class="span4 columns course-list-sidebar-wrapper">
      <CourseList :courses="courses"/>
    </div>
</div>
</template>
