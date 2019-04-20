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
import CourseFilterSublist from "./CourseFilterSublist.vue";
import CourseFilterSemester from "./CourseFilterSemester.vue";
import CourseFilterName from "./CourseFilterName.vue";
import { CourseShell, Group, Course } from "../models";

@Component({
  components: {
    CourseFilterSublist,
    CourseFilterSemester,
    CourseFilterName,
  },
  props: {
    hideSemester:Boolean as ()=>Boolean,
  },
  computed: {
    ...mapGetters("courses", {
      allTypes:"allTypes",
      allTags:"allTags",
      allEffects:"allEffects",
      allSemesters:"allSemesters",
    }),
    ...mapGetters("filters", {
      activeFilter:"activeFilter",
      semester:"semester",
      name:"name",
    })
  },
  data: ()=>({
    extended:false,
    toggleMsg:"⇩ więcej ⇩"
  }),
  methods:{
    toggle:function (){
      this.$data.extended = !this.$data.extended;
      this.$data.toggleMsg = this.$data.extended ? "⇧ mniej ⇧" : "⇩ więcej ⇩";
    }
  }

})
export default class CourseFilter extends Vue {
  
}
</script>

<template>
  <div class="full-width">
    <div :class="'flex-row full-width extendable ' + (extended ? 'extended' : 'not-extended')">
      <div class="third vert-list">
        <CourseFilterSublist :activeFilter="activeFilter" filterId="types" title="Rodzaje" :allAvaiable="allTypes" />
      </div>
      <div class="third vert-list">
        <CourseFilterSublist :activeFilter="activeFilter" filterId="effects" title="Efekty" :allAvaiable="allEffects" />
      </div>
      <div class="third vert-list">
        <CourseFilterName :name="name"/>
        <CourseFilterSemester v-if="!hideSemester" :allAvaiable="allSemesters" :selected="semester"/>
        <CourseFilterSublist :activeFilter="activeFilter" filterId="tags" title="Tagi" :allAvaiable="allTags" />
      </div>
    </div>
    <div class="expansion-toggle" v-on:click="toggle">
      <hr/>
      <h5>{{toggleMsg}}</h5>
      <hr/>
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
.extendable{
  max-height: 40rem;
  transition: 100ms;
}
.not-extended{
  max-height: 7rem;
  overflow-y: hidden;
}
.expansion-toggle{
  text-align: center;
}
</style>
