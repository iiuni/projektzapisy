<script lang="ts">
import { computed, defineComponent, ref } from "vue";
import type { ComputedRef, PropType } from "vue";

interface Poll {
  id: string;
  hours: string;
  type: string;
  name: string;
  number_of_submissions: number;
  is_own: boolean;
}

export default defineComponent({
  props: {
    polls: {
      type: Object as PropType<Record<string, Record<string, Poll[]>>>,
      required: true,
    },
    submissionsCount: {
      type: Object as PropType<Record<string, number>>,
      required: true,
    },
    currentPoll: {
      type: Object as PropType<Poll | null>,
      required: true,
    },
    isSuperuser: {
      type: Boolean,
      required: true,
    },
    selectedSemester: {
      type: Object as PropType<{ id: String }>,
      required: true,
    },
  },
  methods: {
    orderEntriesAlph: function (polls: Poll[]) {
      return [...polls].sort((a: Poll, b: Poll) =>
        a.name.localeCompare(b.name)
      );
    },
  },

  setup(props) {
    const allPolls = props.polls;
    const showOnlyMyCourses = ref(false);

    const myPolls: ComputedRef<Record<string, Record<string, Poll[]>>> =
      computed(() => {
        return Object.fromEntries(
          Object.entries(allPolls).filter(([course_name, course_polls]) => {
            if (course_name === "Ankiety ogólne") return true;
            return Object.entries(course_polls).some(
              ([group_key, group_polls]) => {
                return group_polls.some((poll) => poll.is_own);
              }
            );
          })
        );
      });

    return {
      allPolls,
      myPolls,
      showOnlyMyCourses,
    };
  },
});
</script>

<template>
  <div>
    <div
      v-if="isSuperuser"
      style="display: flex; align-items: center"
      class="mb-3"
    >
      <label style="display: flex; align-items: center">
        <input
          type="checkbox"
          v-model="showOnlyMyCourses"
          style="margin-right: 10px"
        />
        Pokaż tylko ankiety dotyczące moich grup i przedmiotów
      </label>
    </div>
    <div class="accordion" id="course-sections">
      <div
        v-for="(course_polls, course_name, index) in showOnlyMyCourses
          ? myPolls
          : allPolls"
        :key="course_name"
        class="accordion-item"
      >
        <button
          class="accordion-button collapsed"
          style="cursor: pointer"
          :id="'course-section-' + index + '-heading'"
          data-bs-toggle="collapse"
          :data-bs-target="'#course-section-' + index"
          aria-expanded="false"
          :aria-controls="'course-section-' + index"
        >
          <div class="d-flex w-100 justify-content-between me-1">
            <span>{{ course_name }}</span>
            <span class="text-end text-nowrap align-self-center">{{
              submissionsCount[course_name] || "Brak"
            }}</span>
          </div>
        </button>
        <div
          class="border-top collapse list-group list-group-flush"
          :class="{ show: currentPoll && currentPoll.type === course_name }"
          :id="'course-section-' + index"
          :aria-labelledby="'course-section-' + index + '-heading'"
        >
          <template v-for="(group_polls, group_key) in course_polls">
            <a
              v-for="(poll, poll_key) in orderEntriesAlph(group_polls)"
              :key="group_key + '-' + poll_key"
              :href="
                '/grade/poll/results/semester/' +
                selectedSemester.id +
                '/poll/' +
                poll.id +
                '/'
              "
              class="list-group-item list-group-item-action"
              :class="{ active: currentPoll && poll.id === currentPoll.id }"
            >
              <div class="d-flex w-100 justify-content-between">
                <span class="inline" v-if="group_polls.length > 1">
                  {{ poll.name }} ({{ poll.hours }})
                </span>
                <span class="inline" v-else>
                  {{ poll.name }}
                </span>

                <span class="text-end text-nowrap">{{
                  poll.number_of_submissions
                }}</span>
              </div>
            </a>
          </template>
        </div>
      </div>
      <div v-if="Object.keys(allPolls).length === 0" class="alert alert-info">
        Brak przesłanych ankiet w wybranym semestrze.
      </div>
    </div>
  </div>
</template>
