<script lang="ts">
import { defineComponent, ref } from "vue";

interface Poll {
  id: string;
  type: string;
  name: string;
  number_of_submissions: number;
  is_own: boolean;
}

export default defineComponent({
  props: {
    polls: {
      type: Object as () => Record<string, Poll[]>,
      required: true,
    },
    submissionsCount: {
      type: Object,
      required: true,
    },
    currentPoll: {
      type: Object as () => Poll | null,
      default: null,
    },
    isSuperuser: {
      type: Boolean,
      required: true,
    },
  },
  setup(props) {
    const fullList = ref(props.polls);
    const currentList = ref(fullList.value);
    const showOnlyMyCourses = ref(false);

    const updateCurrentList = () => {
      if (showOnlyMyCourses.value) {
        let filteredCourses: Record<string, Poll[]> = {};

        Object.keys(fullList.value).forEach((key) => {
          let category = fullList.value[key];
          if (key == "Ankiety ogólne") {
            filteredCourses[key] = category;
          } else {
            let filteredCategory = category.filter(
              (poll: Poll) => poll.is_own === true
            );

            if (filteredCategory.length > 0) {
              filteredCourses[key] = filteredCategory;
            }
          }
        });
        currentList.value = filteredCourses;
      } else {
        currentList.value = fullList.value;
      }
    };

    return {
      fullList,
      currentList,
      showOnlyMyCourses,
      updateCurrentList,
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
          @change="updateCurrentList"
          style="margin-right: 10px"
        />
        Pokaż tylko ankiety dotyczące moich grup i przedmiotów
      </label>
    </div>
    <div class="accordion" id="course-sections">
      <div
        v-for="(entries, group_name, index) in currentList"
        :key="group_name"
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
            <span>{{ group_name }}</span>
            <span class="text-end text-nowrap align-self-center">{{
              submissionsCount[group_name] || 0
            }}</span>
          </div>
        </button>
        <div
          class="border-top collapse list-group list-group-flush"
          :class="{ show: currentPoll && currentPoll.type === group_name }"
          :id="'course-section-' + index"
          :aria-labelledby="'course-section-' + index + '-heading'"
        >
          <a
            v-for="entry in entries"
            :key="entry.id"
            :href="entry.href"
            class="list-group-item list-group-item-action"
            :class="{ active: currentPoll && entry.id === currentPoll.id }"
          >
            <div class="d-flex w-100 justify-content-between">
              <span>{{ entry.name }}</span>
              <span class="text-end text-nowrap">{{
                entry.number_of_submissions
              }}</span>
            </div>
          </a>
        </div>
      </div>
      <div
        v-if="Object.keys(currentList).length === 0"
        class="alert alert-info"
      >
        Brak przesłanych ankiet w wybranym semestrze.
      </div>
    </div>
  </div>
</template>
