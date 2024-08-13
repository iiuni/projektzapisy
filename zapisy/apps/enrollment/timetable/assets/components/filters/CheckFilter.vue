<script setup lang="ts">
import { property } from "lodash";
import { Filter } from "../../store/filters";
import { ref, watch } from "vue";
import { useStore } from "vuex";
const store = useStore();

class BooleanFilter implements Filter {
  constructor(public on: boolean, public propertyName: string) {}

  visible(c: Object): boolean {
    if (!this.on) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => boolean;
    let propValue = propGetter(c);
    return propValue;
  }
}

const props = defineProps<{
  property: string;
  filterKey: string;
  label: string;
}>();

const on = ref(false);

const searchParams = new URL(window.location.href).searchParams;
if (searchParams.has(props.property)) {
  if (searchParams.get(props.property) === "true") {
    on.value = true;
  }
}

store.subscribe((mutation) => {
  switch (mutation.type) {
    case "filters/clearFilters":
      on.value = false;
      break;
  }
});

watch(
  on,
  (newOn) => {
    const url = new URL(window.location.href);
    if (newOn) {
      url.searchParams.set(props.property, newOn.toString());
    } else {
      url.searchParams.delete(props.property);
    }
    window.history.replaceState(null, "", url.toString());
    store.commit("filters/registerFilter", {
      k: props.filterKey,
      f: new BooleanFilter(on.value, props.property),
    });
  },
  { immediate: true }
);
</script>

<template>
  <div class="input-group">
    <div class="custom-control custom-checkbox">
      <input
        type="checkbox"
        class="custom-control-input"
        :id="filterKey"
        v-model="on"
      />
      <label class="custom-control-label" :for="filterKey">{{ label }}</label>
    </div>
  </div>
</template>
