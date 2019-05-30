<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";

import { CourseShell, Group, Course } from "../models";

@Component({
  props: {
    title: String as ()=>String,
    filterId: String as ()=>String,
	 	allAvaiable: Array as ()=>String[],
    activeFilter: Function as ()=>Function, 
  },
})
export default class CourseFilterSublist extends Vue {
  // The computed property selectionState comes from store.
  get selection(): string[] {
		const selectionState = this.$props.activeFilter(this.$props.filterId);
		console.info("CourseFilterList getter:",selectionState)
		return selectionState;
		//"avaiable.split(' ').join('')"
  }
  set selection(value: string[]) {
		console.info("CourseFilterList setter:",value)
    this.$store.dispatch("filters/updateFilter", [this.$props.filterId,value]);
  }
}
</script>

<template>
	<div class="vert-list">
		<h4>{{title}}</h4>
		<div 
		class="form-check" 
		v-for="avaiable in allAvaiable"
		v-bind:key="avaiable"
		>
			<input type="checkbox" :id="avaiable" :value="avaiable" v-model="selection">
			<label class="form-check-label">
				{{avaiable}}
			</label>
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
