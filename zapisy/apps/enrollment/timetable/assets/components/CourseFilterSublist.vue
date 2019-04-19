<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";

import { CourseShell, Filter, Group, Course } from "../models";

@Component({
  props: {
    title: String as ()=>String,
    filterId: String as ()=>String,
	 allAvaiable: Array as ()=>String[],
	 filter: Filter,
  },
  computed: mapGetters("courses", {
    activeFilter:"activeFilter"
  }),
})
export default class CourseFilterSublist extends Vue {
  actives: number[];
  get active(): number[] {
    return this.actives;
  }
  set active(value: number[]) {
	 this.$props.filter.manyValue = value;
    this.$store.dispatch("courses/updateFilter", [this.$props.filterId,this.$props.filter]);
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
			<input class="form-check-input" 
					 v-model="active" 
					 type="checkbox"
					 v-bind:id="avaiable.split(' ').join('')"
					 v-bind:value="activeFilter(filterId).manyValue.has(tag)"
			/> 
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
