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
  computed: {
    ...mapGetters("courses", {
      activeFilters:"activeFilters",
      activeFilter:"activeFilter",
      allTypes:"allTypes",
      allTags:"allTags",
      allEffects:"allEffects",
    })
  }
})
export default class CourseFilter extends Vue {
 extended=false
}
</script>

<template>
    <div class="flex-row full-width">
      <div class="third vert-list">
        <div class="vert-list">
          <h4>Tagi:</h4>
          <div 
            class="form-check" 
            v-for="tag in allTags"
            v-bind:key="tag"
          >
            <input class="form-check-input" v-on:click="handleTag($event)" type="checkbox" v-bind:value="activeFilter('tagi').manyValue.has(tag)"/> 
            <label class="form-check-label">
              {{tag}}
            </label>
          </div>
        </div>
      </div>
      <div class="third vert-list">
        <div class="vert-list">
        </div>
      </div>
      <div class="third vert-list">
        <div class="vert-list">
        </div>
      </div>
    </div>
</template>

<style lang="scss" scoped>
.flex-row{
  display: flex;
  flex-direction: row;
  justify-content: space-between;
}
.third{
  width: 33%;
}
.vert-list{
  display: flex;
  flex-direction: column;
}
.full-width{
  width: 100%;
}
</style>
