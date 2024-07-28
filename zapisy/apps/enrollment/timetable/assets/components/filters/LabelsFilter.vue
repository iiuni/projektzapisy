<script setup lang="ts">
import { property, intersection, isEmpty, keys, fromPairs } from "lodash";
import { Filter } from "../../store/filters";
import { KVDict } from "../../models";
import { computed, ref } from "vue";

import { useStore } from "vuex";
const store = useStore();

class IntersectionFilter implements Filter {
  constructor(public ids: number[] = [], public propertyName: string) {}

  visible(c: Object): boolean {
    if (isEmpty(this.ids)) {
      return true;
    }
    const propGetter = property(this.propertyName) as (c: Object) => number[];
    const propValue = propGetter(c);
    const common = intersection(this.ids, propValue);
    return !isEmpty(common);
  }
}

const props = defineProps<{
  property: string;
  filterKey: string;
  allLabels: KVDict;
  title: string;
  onClass: string;
}>();

const allLabelIds = computed(() => {
  return keys(props.allLabels).map((id) => parseInt(id, 10));
});
const selected = ref<{ [k: number]: boolean }>({});

const toggle = (id: number) => {
  selected.value[id] = !selected.value[id];
  afterSelectionChanged();
};

const afterSelectionChanged = () => {
  const selectedIds = allLabelIds.value.filter((id) => selected.value[id]);

  const url = new URL(window.location.href);
  if (selectedIds.length > 0) {
    url.searchParams.set(props.property, selectedIds.join(","));
  } else {
    url.searchParams.delete(props.property);
  }
  window.history.replaceState(null, "", url.toString());

  store.commit("filters/registerFilter", {
    k: props.filterKey,
    f: new IntersectionFilter(selectedIds, props.property),
  });
};

// When the component is created we set all the labels as unselected
// and then set those specified in the query string as selected.
selected.value = fromPairs(allLabelIds.value.map((k) => [k, false]));

const searchParams = new URL(window.location.href).searchParams;
if (searchParams.has(props.property)) {
  const selectedIds = searchParams
    .get(props.property)!
    .split(",")
    .map((id) => parseInt(id, 10))
    .filter((id) => !isNaN(id));

  selectedIds.forEach((id) => (selected.value[id] = true));

  store.commit("filters/registerFilter", {
    k: props.filterKey,
    f: new IntersectionFilter(selectedIds, props.property),
  });
}

store.subscribe((mutation) => {
  if (mutation.type === "filters/clearFilters") {
    allLabelIds.value.forEach((id) => {
      selected.value[id] = false;
    });
    afterSelectionChanged();
  }
});
</script>

<template>
  <div class="mb-3 overflow-hidden">
    <h4>{{ title }}</h4>
    <a
      href="#"
      v-for="l in allLabelIds"
      class="badge"
      v-bind:class="[selected[l] ? onClass : 'bg-secondary']"
      @click.prevent="toggle(l)"
    >
      {{ allLabels[l] }}
    </a>
  </div>
</template>
