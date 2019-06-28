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
import CourseFilterOwner from "./CourseFilterOwner.vue";
import CourseFilterName from "./CourseFilterName.vue";
import { CourseShell, Group, Course } from "../models";

@Component({
  components: {
    CourseFilterSublist,
    CourseFilterSemester,
    CourseFilterName,
    CourseFilterOwner,
  },
  props: {
    hidesemester:String as ()=>any,
  },
  computed: {
    ...mapGetters("courses", {
      allTypes:"allTypes",
      allProps:"allProps",
      allTags:"allTags",
      allEffects:"allEffects",
      allSemesters:"allSemesters",
      allOwners:"allOwners",
    }),
    ...mapGetters("filters", {
      activeFilter:"activeFilter",
      semester:"semester",
      owner:"owner",
      name:"name",
    })
  },
  data: ()=>({
    extended:false,
  }),
  methods:{
    toggle:function (){
      this.$data.extended = !this.$data.extended;
    },
    mapProps:function(id){
      if(id==="exam") return "Zakończone egzaminem";
      if(id==="english") return "W języku Angielskim";
      if(id==="firstYearFriendly") return "Polecane dla pierwszego roku";
      return id;
    }
  }

})
export default class CourseFilter extends Vue {
  
}
</script>

<template>
  <div class="jumbotron">
    <div :class="'row extendable ' + (extended ? 'extended' : 'not-extended')">
      <div class="col-xs-12 col-sm-4 vert-list">
        <CourseFilterName :name="name"/>
        <CourseFilterSublist :activeFilter="activeFilter" filterId="effects" title="Efekty kształcenia" :allAvaiable="allEffects" />
        </div>
      <div class="col-xs-12 col-sm-4 vert-list">
        <CourseFilterSublist :activeFilter="activeFilter" filterId="types" title="Klasyfikacja przedmiotu" :allAvaiable="allTypes" />
      </div>
      <div class="col-xs-12 col-sm-4 vert-list">
        <!-- funkcjonalność wyboru semestru jest ograniczona do filtrowania listy przedmiotów po property "semester" -->
        <!-- <CourseFilterSemester v-if="()=>{console.log('hidesemester',hidesemester); return !hidesemester}" :allAvaiable="allSemesters" :selected="semester"/> -->
        <CourseFilterOwner :allAvaiable="allOwners" :selected="owner"/>
        <CourseFilterSublist :activeFilter="activeFilter" :labelMap="mapProps" filterId="props" title="Inne cechy przedmiotu" :allAvaiable="allProps" />
        <CourseFilterSublist :activeFilter="activeFilter" filterId="tags" title="Tagi magisterskie" :allAvaiable="allTags" />
      </div>
    </div>
    <div v-if="extended" class="expansion-toggle" v-on:click="toggle">
      <h5>
        <font-awesome-icon icon="chevron-up"/>
        <span class="expansion-toggle-text">ukryj filtry</span>
        <font-awesome-icon icon="chevron-up"/>
      </h5>
    </div>
    <div v-if="!extended" class="expansion-toggle" v-on:click="toggle">
      <h5>
        <font-awesome-icon icon="chevron-down"/>
        <span class="expansion-toggle-text">pokaż wszystkie filtry</span>
        <font-awesome-icon icon="chevron-down"/>
      </h5>
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
@media (min-width: 576px) {
  .vert-list>*:first-child{
    margin-top: 0;
  }  
}
.vert-list>*{
  margin-top: 1.15rem;
}
.full-width{
  width: 100%;
}
.extendable{
  height: auto;
  transition: 100ms;
}
.not-extended{
  height: 9rem;
  overflow-y: hidden;
}
.expansion-toggle{
  text-align: center;
  cursor: pointer;
  padding: 1rem 0 0 0;
}
.expansion-toggle-text{
  margin: 0 0.5rem;
}
.jumbotron{
  padding: 2rem 1rem;
}
</style>
