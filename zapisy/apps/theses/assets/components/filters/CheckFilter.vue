<script lang="ts" setup>
import { property } from "lodash";

import { getCurrentInstance, ref, watch } from "vue";
// TODO: use store from vuex4
const useStore = () => {
  const vm = getCurrentInstance();
  if (!vm) throw new Error("must be called in setup");
  return vm.proxy!.$store;
};
const store = useStore();

interface Filter {
  visible(c: object): boolean;
}

class BooleanFilter implements Filter {
  constructor(public on: boolean, public propertyName: string) {}

  visible(c: object): boolean {
    if (!this.on) {
      return true;
    }
    const propGetter = property(this.propertyName) as (c: object) => boolean;
    return propGetter(c);
  }
}

const props = defineProps<{
  property: string;
  filterKey: string;
  label: string;
}>();

const on = ref(false);

watch(on, (newOn: boolean) => {
  store.commit("filters/registerFilter", {
    k: props.filterKey,
    f: new BooleanFilter(newOn, props.property),
  });
});
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
