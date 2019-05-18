<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";

import { CourseShell, Group, Course } from "../models";

@Component({
  props: {
		allAvaiable: Array as ()=>string[],
		owner: String as ()=>string,
	},
})
export default class CourseFilterSemester extends Vue {
  // The computed property selectionState comes from store.
  get selection(): string {
		return this.$props.owner;
  }
  set selection(value: string) {
    this.$store.dispatch("filters/setFilter", ["owner",value]);
  }
}
</script>

<template>
	<div class="form-group">
		<h4>Organizator przedmiotu</h4>
    <select class="form-control" v-model="selection" id="exampleFormControlSelect2">
      <option v-bind:key="avaiable" v-for="avaiable in allAvaiable">{{avaiable}}</option>
    </select>
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
