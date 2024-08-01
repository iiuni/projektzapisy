<script lang="ts">
import { defineComponent, ref } from "vue";
import type { PropType } from "vue";

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
    selectedSemesterId: {
      type: Number,
      required: true,
    },
  },
  setup(props: any) {
    const polls: Record<string, Record<string, Poll[]>> = props.polls;

    const myCoursesForSuperUser = new Set<string>();
    var lastOwnPoll = "";
    if (props.isSuperuser) {
      Object.entries(polls).map(([course_name, course_polls]) => {
        Object.entries(course_polls).map(([group_name, group_polls]) => {
          group_polls.map((poll) => {
            if (poll.is_own) {
              myCoursesForSuperUser.add(course_name);
              lastOwnPoll = course_name;
            }
          });
        });
      });
    }

    const allPolls: Record<string, Record<string, Poll[]>> = Object.fromEntries(
      Object.entries(polls).map(([course_name, course_polls]) => {
        return [
          course_name,
          Object.fromEntries(
            Object.entries(course_polls).map(([group_name, group_polls]) => {
              return [group_name, group_polls];
            })
          ),
        ];
      })
    );

    const showOnlyMyCourses = ref(false);

    return {
      allPolls,
      showOnlyMyCourses,
      myCoursesForSuperUser,
      lastOwnPoll,
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
    <transition-group
      name="list"
      tag="div"
      class="accordion"
      id="course-sections"
    >
      <template v-for="(course_polls, course_name, index) in allPolls">
        <div
          v-show="
            showOnlyMyCourses ? myCoursesForSuperUser.has(course_name) : true
          "
          class="accordion-item"
          :class="{
            lastOwnPoll: showOnlyMyCourses && course_name === lastOwnPoll,
          }"
          :key="course_name"
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
            :class="{
              show: currentPoll && currentPoll.type === course_name,
            }"
            :id="'course-section-' + index"
            :aria-labelledby="'course-section-' + index + '-heading'"
          >
            <template v-for="group_polls in course_polls">
              <template v-for="poll in group_polls">
                <a
                  v-if="showOnlyMyCourses ? poll.is_own : true"
                  :key="poll.id"
                  :href="
                    '/grade/poll/results/semester/' +
                    selectedSemesterId +
                    '/poll/' +
                    poll.id +
                    '/'
                  "
                  class="list-group-item list-group-item-action"
                  :class="{ active: currentPoll && poll.id === currentPoll.id }"
                >
                  <div class="d-flex w-100 justify-content-between">
                    <span v-if="group_polls.length >= 2" class="inline">
                      {{ poll.name }} ({{ poll.hours }})
                    </span>
                    <span v-else class="inline">
                      {{ poll.name }}
                    </span>
                    <span class="text-end text-nowrap">{{
                      poll.number_of_submissions
                    }}</span>
                  </div>
                </a>
              </template>
            </template>
          </div>
        </div>
      </template>
    </transition-group>
    <div v-if="Object.keys(allPolls).length === 0" class="alert alert-info">
      Brak przesłanych ankiet w wybranym semestrze.
    </div>
  </div>
</template>

<style scoped>
.lastOwnPoll {
  border-bottom-right-radius: var(--bs-accordion-inner-border-radius);
  border-bottom-left-radius: var(--bs-accordion-inner-border-radius);
  overflow: hidden;
}
</style>
