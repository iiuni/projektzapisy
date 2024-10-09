<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import { CourseInfo } from "../store/courses";
import Component from "vue-class-component";

@Component({
  computed: {
    ...mapGetters("courses", {
      courses: "courses",
    }),
    ...mapGetters("filters", {
      tester: "visible",
    }),
    ...mapGetters("sorting", {
      compare: "compare",
    }),
  },
})
export default class StatisticsList extends Vue {
  coursesList: CourseInfo[] = [];

  courses!: CourseInfo[];
  tester!: (_: CourseInfo) => boolean;
  compare!: (a: CourseInfo, b: CourseInfo) => number;

  created() {
    this.$store.dispatch("courses/initFromJSONTag");
  }
  mounted() {
    this.coursesList = this.courses;
    this.coursesList.sort(this.compare);

    this.$store.subscribe((mutation, state) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.coursesList.sort(this.compare);
          break;
        case "sorting/changeSorting":
          this.coursesList.sort(this.compare);
          break;
      }
    });
  }
}
</script>

<template>
  <table class="table table-striped">
    <thead class="text-muted">
      <tr>
        <th scope="col">Prowadzący</th>
        <th scope="col">Typ</th>
        <th scope="col">Miejsca</th>
        <th scope="col">Zapisani</th>
        <th scope="col">Kolejka</th>
        <th scope="col">Przypięci</th>
        <th></th>
      </tr>
    </thead>
    <tbody>
      <template v-for="course in coursesList">
        <tr v-show="tester(course)">
          <th colspan="2">
            {{ course.course_name }}
          </th>
          <td colspan="6">
            <span
              v-for="waiting_course in course.waiting_students"
              class="badge bg-danger"
              title="Oczekujących niezapisanych"
              style="margin-right: 5px"
            >
              {{ waiting_course.name }}
              <span class="badge bg-light text-dark">
                {{ waiting_course.number }}
              </span>
            </span>
          </td>
        </tr>
        <tr
          v-for="group in course.groups"
          :key="group.id"
          v-show="tester(course)"
        >
          <td>{{ group.teacher_name }}</td>
          <td>{{ group.type_name }}</td>
          <td>
            {{ group.limit }}
            <template v-for="gs in group.guaranteed_spots">
              +
              <span :title="'Miejsca gwarantowane dla grupy ' + gs.name + '.'">
                {{ gs.limit }}
              </span>
            </template>
          </td>
          <td>{{ group.enrolled }}</td>
          <td>{{ group.queued }}</td>
          <td>{{ group.pinned }}</td>
          <td>
            <a class="badge bg-primary" :href="group.url" target="_blank">
              Admin <i class="fas fas-sm fa-external-link-alt"></i>
            </a>
          </td>
        </tr>
      </template>
    </tbody>
  </table>
</template>
