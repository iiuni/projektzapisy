<script lang="ts">
// The CourseFilter component allows the student to select courses presented on
// prototype.
//
// The selection is not persistent. In order to keep a group on prototype the
// student will need to _pin_ it. The state is not maintained by the component.
// This job is handled by the Vuex store (`../store/courses.ts`).
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";

import { CourseShell, Filter, Group, Course } from "../models";

@Component({
  props: {
  },
  computed: mapGetters("courses", {
    activeFilters:"activeFilters",
    allTypes:"allTypes",
    allTags:"allTags",
    allEffects:"allEffects",
  })
})
export default class CourseFilter extends Vue {
 extended=false
}
</script>

<template>
  <div class="course-list-wrapper">
    <div><h3>Filtry są fajne</h3></div>
    <div v-bind:class='extended ? "extendable extended" : "extendable"'>
      
      
    </div>
    <div v-on:click='extended = !extended'>And this one is like forever</div>
  </div>
</template>

<style lang="scss" scoped>
.extendable{
  max-height: 4rem;
  overflow: hidden;
}
.extended{
  max-height: unset;
}
.flex-row{
  display: flex;
  flex-direction: row;
}
</style>
