<script setup lang="ts">
import { property } from "lodash";
import { CourseInfo } from "../../store/courses";
import { Filter } from "../../store/filters";
import { ref, watch } from "vue";
import { useStore } from "vuex";
const store = useStore();

class TextFilter implements Filter {
  constructor(public pattern: string = "", public propertyName: string) {}

  visible(c: CourseInfo): boolean {
    let propGetter = property(this.propertyName) as (c: CourseInfo) => string;
    let propValue = propGetter(c);
    return propValue
      .toLocaleLowerCase()
      .includes(this.pattern.toLocaleLowerCase());
  }
}

const props = defineProps<{
  property: string;
  filterKey: string;
  placeholder: string;
}>();

const pattern = ref("");

const searchParams = new URL(window.location.href).searchParams;

if (searchParams.has(props.property)) {
  // TypeScript doesn't infer that property is present, manual cast required.
  pattern.value = searchParams.get(props.property) as string;
}

store.subscribe((mutation) => {
  switch (mutation.type) {
    case "filters/clearFilters":
      pattern.value = "";
      break;
  }
});

watch(pattern, (newPattern: string) => {
  const url = new URL(window.location.href);
  if (newPattern.length == 0) {
    url.searchParams.delete(props.property);
  } else {
    url.searchParams.set(props.property, newPattern);
  }
  window.history.replaceState(null, "", url.toString());

  store.commit("filters/registerFilter", {
    k: props.filterKey,
    f: new TextFilter(newPattern, props.property),
  });
});
</script>

<template>
  <div class="input-group mb-2">
    <input
      class="form-control"
      type="text"
      v-model="pattern"
      :placeholder="placeholder"
    />
    <button
      class="btn btn-outline-secondary"
      type="button"
      @click="pattern = ''"
    >
      &times;
    </button>
  </div>
</template>
