<script lang="ts">
import Vue from "vue";
// import { mapGetters } from "vuex";
import Component from "vue-class-component";
// import { getCurrentInstance } from "vue";

// const current = getCurrentInstance();
import { DayOfWeek, nameDay, Group, Course } from "../models";

// export type CourseObject = { id: number; name: string; url: string };
const SimpleSummaryProps = Vue.extend({
  props: {
    summaryType: {
      type: String,
      default: "",
    },
    sumPoints: {
      type: Number as () => Number,
      default: 0,
    },
    groups: {
      type: Array as () => Array<Group>,
      default: {},
    },
    courses: {
      type: Object as () => Object,
      default: {},
    },
    groupsCondition: {
      type: Function,
      deafult: (group: Group, course: Course) => Boolean,
    },
  },
});
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
export default class SimpleSummary extends SimpleSummaryProps {
  // The computed property selectionState comes from store.
  //   selectionState!: number[];
  //   // The same goes for courses and tester.
  //   courses!: CourseInfo[];
  //   tester!: (_: CourseInfo) => boolean;

  //   get sumPoints(): number {
  //     return state.state.sumPoints;
  //   }
  //   get courses(): { [id: number]: Course } {
  //     return state.state.courses;
  //   }
  //   get groups(): { [id: number]: Group } {
  //     return values(state.state.store).filter(
  //       (g) => g.isEnrolled || g.isEnqueued || g.isPinned || g.isSelected
  //     );
  //   }
  public GetNameDay(day: DayOfWeek) {
    return nameDay(day);
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
          <td>
            <strong>Suma punktów ECTS za {{ summaryType }}:</strong>
          </td>
          <td class="ects">{{ sumPoints }}</td>
        </tr>
      </tfoot>
      <tbody v-for="(item, idx) in courses" :value="item" :key="idx">
        <tr class="courseHeader">
          <td class="name" scope="col">
            <a href="{% url 'course-page' course.grouper.slug %}">
              {{ item.name }}
            </a>
          </td>
          <td rowspan="2" class="ects">
            {{ item.summaryPoints }}
          </td>
        </tr>
        <tr class="courseDetails">
          <td>
            <ul v-for="(group, gid) in groups" :value="group" :key="gid">
              <li v-if="groupsCondition(group, item)">
                <span class="type">{{ group.type }}:</span>
                <span class="term">
                  {{ GetNameDay(group.terms[0].weekday) }}
                  {{ group.terms[0].startTimeString }}-{{
                    group.terms[0].endTimeString
                  }}
                </span>
                <span class="classroom"
                  >sala:
                  {{ group.terms[0].getClassrooms }}
                </span>
              </li>
            </ul>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
