<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import SorterField from "./sorters/SorterField.vue";
import { ThesisInfo } from "../store/theses";

import { getCurrentInstance } from "vue";
const useStore = () => {
  const vm = getCurrentInstance();
  if (!vm) throw new Error("must be called in setup");
  return vm.proxy.$store;
};
const store = useStore();

const theses = computed(() => store.getters["theses/theses"]);
const tester = computed(() => store.getters["filters/visible"]);
const compare = computed(() => store.getters["sorting/compare"]);

const visibleTheses = ref<ThesisInfo[]>([]);

store.dispatch("theses/initFromJSONTag");

onMounted(() => {
  visibleTheses.value = theses.value.sort(compare.value);

  store.subscribe((mutation: { type: string }) => {
    switch (mutation.type) {
      case "filters/registerFilter":
      case "sorting/changeSorting":
        visibleTheses.value = theses.value.filter(tester.value);
        visibleTheses.value.sort(compare.value);
        break;
    }
  });
});

const reservedUntilAltText = (thesis: ThesisInfo): string | undefined => {
  if (!thesis.reserved_until) {
    return undefined;
  }
  return `Zarezerwowana do ${thesis.reserved_until}`;
};
</script>
<style scoped>
.selection-none {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
</style>

<template>
  <table class="table table-hover selection-none table-responsive-md">
    <thead id="table-header">
      <tr class="text-center">
        <th>
          <SorterField property="title" label="Tytuł" />
        </th>
        <th>
          <SorterField property="kind" label="Typ" />
        </th>
        <th>
          <SorterField property="advisor_last_name" label="Promotor" />
        </th>
        <th>Rezerwacja</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="thesis of visibleTheses" :key="thesis.id">
        <td class="align-middle">
          <a class="btn-link" :href="thesis.url">{{ thesis.title }}</a>
          <em v-if="thesis.status !== 'zaakceptowana'" class="text-muted"
            >({{ thesis.status }})</em
          >
        </td>
        <td class="text-center align-middle">
          {{ thesis.kind }}
        </td>
        <td class="align-middle">
          {{ thesis.advisor }}
        </td>
        <td
          class="align-middle"
          :class="{ 'text-muted': thesis.is_available }"
          :title="reservedUntilAltText(thesis)"
        >
          {{ thesis.students }}
        </td>
      </tr>
      <tr v-if="!visibleTheses.length" class="text-center">
        <td colspan="4">
          <em class="text-muted">Brak prac dyplomowych.</em>
        </td>
      </tr>
    </tbody>
  </table>
</template>
