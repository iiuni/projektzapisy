<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";

import { CourseShell, Group, Course } from "../models";

@Component({
  props: {
		name: String as ()=>string,
	},
})
export default class CourseFilterName extends Vue {
  // The computed property selectionState comes from store.
  get selection(): string {
		return this.$props.name;
  }
  set selection(value: string) {
    this.$store.dispatch("filters/setFilter", ["name",value]);
  }
}
</script>

<template>
	<div class="form-group">
		<h4>Nazwa przedmiotu</h4>
    <input type="text" v-model="selection" class="form-control" placeholder="np. Algebra">
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
