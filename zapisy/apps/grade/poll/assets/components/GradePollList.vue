<script setup lang="ts">
import { ref } from "vue";
import type { PropType } from "vue";

interface Poll {
  id: string;
  hours: string;
  type: string;
  name: string;
  number_of_submissions: number;
  is_own: boolean;
}

const props = defineProps({
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
});

function orderEntriesAlph(polls: Poll[]) {
  return polls.sort((a: Poll, b: Poll) => a.name.localeCompare(b.name));
}

const set_of_my_courses = new Set<string>();
Object.entries(props.polls).map(([course_name, course_polls]) => {
  Object.entries(course_polls).map(([group_name, group_polls]) => {
    group_polls.map((poll) => {
      if (poll.is_own) {
        set_of_my_courses.add(course_name);
      }
    });
  });
});

const showOnlyMyCourses = ref(false);

const allPolls: Record<string, Record<string, Poll[]>> = Object.fromEntries(
  Object.entries(props.polls).map(([course_name, course_polls]) => {
    return [
      course_name,
      Object.fromEntries(
        Object.entries(course_polls).map(([group_name, group_polls]) => {
          return [group_name, orderEntriesAlph(group_polls)];
        })
      ),
    ];
  })
);
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
      <template v-for="(course_polls, course_name, index) in allPolls">
        <div
          v-show="showOnlyMyCourses ? set_of_my_courses.has(course_name) : true"
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
                submissionsCount[course_name] || 0
              }}</span>
            </div>
          </button>
          <div
            class="border-top collapse list-group list-group-flush"
            :class="{ show: currentPoll && currentPoll.type === course_name }"
            :id="'course-section-' + index"
            :aria-labelledby="'course-section-' + index + '-heading'"
          >
            <template v-for="group_polls in course_polls">
              <a
                v-for="poll in group_polls"
                :key="poll.id"
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
      </template>
      <div v-if="Object.keys(allPolls).length === 0" class="alert alert-info">
        Brak przesłanych ankiet w wybranym semestrze.
      </div>
    </div>
  </div>
</template>
