<template>
  <div class="accordion" id="course-sections">
    <div v-if="isSuperuser" style="display: flex; align-items: center">
      <input
        type="checkbox"
        v-model="showOnlyMyCourses"
        @change="updateCurrentList"
        style="margin-right: 10px"
      />
      <label>Pokaż tylko ankiety dotyczące moich grup i przedmiotów</label>
    </div>
    <div
      v-for="(entries, group_name, index) in currentList"
      :key="group_name"
      class="card"
    >
      <div
        class="card-header"
        :id="'course-section-' + index + '-heading'"
        data-toggle="collapse"
        :data-target="'#course-section-' + index"
        aria-expanded="false"
        :aria-controls="'course-section-' + index"
      >
        <div class="d-flex w-100 justify-content-between">
          <span>{{ group_name }}</span>
          <span class="text-right text-nowrap">{{
            submissionsCount[group_name] || 0
          }}</span>
        </div>
      </div>
      <div
        class="border-top collapse list-group list-group-flush"
        :class="{ show: currentPoll && currentPoll.category === group_name }"
        :id="'course-section-' + index"
        :aria-labelledby="'course-section-' + index + '-heading'"
      >
        <a
          v-for="entry in entries"
          :key="entry.id"
          :href="
            baseHtml +
            '/grade/poll/results/semester/' +
            selectedSemester.id +
            '/poll/' +
            entry.id
          "
          class="list-group-item list-group-item-action"
          :class="{ active: currentPoll && entry.id === currentPoll.id }"
        >
          <div class="d-flex w-100 justify-content-between">
            <span>{{ entry.subcategory }}</span>
            <span class="text-right text-nowrap">{{
              entry.number_of_submissions
            }}</span>
          </div>
        </a>
      </div>
    </div>
    <div v-if="Object.keys(currentList).length === 0" class="alert alert-info">
      Brak przesłanych ankiet w wybranym semestrze.
    </div>
  </div>
</template>

<script lang="ts">
import Vue from "vue";

export default Vue.extend({
  props: {
    polls: {
      type: Object,
      required: true,
    },
    submissionsCount: {
      type: Object,
      required: true,
    },
    currentPoll: {
      type: Object,
    },
    selectedSemester: {
      type: Object,
      required: true,
    },
    isSuperuser: {
      type: Boolean,
      required: true,
    },
  },
  data() {
    return {
      currentList: {},
      showOnlyMyCourses: false,
      baseHtml: "",
      fullList: {},
    };
  },
  methods: {
    updateCurrentList() {
      if (this.showOnlyMyCourses) {
        let filteredCourses = {};

        Object.keys(this.fullList).forEach((key) => {
          let array = this.fullList[key];
          if (key == "Ankiety ogólne") {
            filteredCourses[key] = array;
          } else {
            let filteredArray = array.filter((poll) => poll.is_own === true);

            if (filteredArray.length > 0) {
              filteredCourses[key] = filteredArray;
            }
          }
        });
        this.currentList = filteredCourses;
      } else {
        this.currentList = this.fullList;
      }
    },
  },
  created() {
    this.fullList = this.polls;
    this.currentList = this.fullList;
    this.baseHtml = `${window.location.protocol}//${window.location.host}`;
  },
});
</script>
