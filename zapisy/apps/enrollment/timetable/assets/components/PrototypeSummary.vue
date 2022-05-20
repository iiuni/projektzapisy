<script lang="ts">
import Vue from "vue";
// import { mapGetters } from "vuex";
import Component from "vue-class-component";
// import { getCurrentInstance } from "vue";

// const current = getCurrentInstance();
import state from "../store/groups";

// export type CourseObject = { id: number; name: string; url: string };
@Component({
  computed: {
    // ...mapGetters("courses", {
      //   sumPointsState: "sumPoints",
    // }),
    // ...mapGetters("filters", {
      //   tester: "visible",
    // }),
  },  
})
export default class PrototypeSummary extends Vue {
  // The computed property selectionState comes from store.
  //   selectionState!: number[];
  //   // The same goes for courses and tester.
  //   courses!: CourseInfo[];
  //   tester!: (_: CourseInfo) => boolean;

  get sumPoints(): number {
    return state.state.sumPoints;
  }
  // set sumPoints(newValue: number): {
  //   state.state.sumPoints = newValue;
  // }  

  // The list should be initialised to contain courses filtered with initial filters
  // fetched from the query string and then apply filters whenever they update.
  //   visibleCourses: CourseInfo[] = [];
  //   methods: {
  // this.visibleCourses = this.courses.filter(this.tester);

  // this.$store.subscribe((mutation, state) => {
  //   switch (mutation.type) {
  //     case "filters/registerFilter":
  //       this.visibleCourses = this.courses.filter(this.tester);
  //       break;
  //   }
  // });
  //   }
}
</script>

<template>
  <div class="table-responsiveVUE">
    <table id="enr-schedule-listByCourseVUE" class="table table-striped">
      <thead>
        <tr>
          <th scope="col">Przedmiot</th>
          <th class="ects" scope="col">ECTS</th>
        </tr>
      </thead>
      <tfoot>
        <tr>
          <td><strong>Suma punktów ECTS:</strong></td>
          <td class="ects">{{ sumPoints }}</td>
        </tr>
      </tfoot>
    </table>
  </div>
</template>
