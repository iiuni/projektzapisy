<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import Component from "vue-class-component";
import { CourseShell, Group, Course } from "../models";

const cancelSelectionText = "-nie wybieraj-";

@Component({
  props: {
		allAvaiable: Array as ()=>string[],
		owner: String as ()=>string,
  },
})
export default class CourseFilterOwner extends Vue {
  get allFinallyAvaiable(): string[]{
    return [cancelSelectionText, ...this.$props.allAvaiable]
  }
  get selection(): string {
		return this.$props.owner;
  }
  set selection(value: string) {
    if(value === cancelSelectionText) value="";
    this.$store.dispatch("filters/setFilter", ["owner",value]);
  }
}
</script>

<template>
	<div class="form-group">
		<h4>Organizator przedmiotu</h4>
    <select class="form-control" v-model="selection" id="exampleFormControlSelect2">
      <option v-bind:key="avaiable" v-for="avaiable in allFinallyAvaiable">{{avaiable}}</option>
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
