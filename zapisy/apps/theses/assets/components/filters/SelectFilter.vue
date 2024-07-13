<script setup lang="ts">
import { property } from "lodash";
import { Filter } from "../../store/filters";

class ExactFilter implements Filter {
  constructor(
    public option: number | string | undefined,
    public propertyName: string
  ) {}

  visible(c: object): boolean {
    if (this.option === undefined) {
      return true;
    }
    const propGetter = property(this.propertyName) as (c: object) => number;
    return propGetter(c) == this.option;
  }
}

const props = defineProps<{
  property: string;
  filterKey: string;
  default?: number | string;
  options: [number | string, string][];
  placeholder: string;
}>();

import { getCurrentInstance, ref, watch } from "vue";
// TODO: use store from vuex4
const useStore = () => {
  const vm = getCurrentInstance();
  if (!vm) throw new Error("must be called in setup");
  return vm.proxy!.$store;
};
const store = useStore();

const selected = ref<number | string | undefined>(props.default);

watch(selected, (newSelected: number | string | undefined) => {
  store.commit("filters/registerFilter", {
    k: props.filterKey,
    f: new ExactFilter(newSelected, props.property),
  });
});
</script>

<template>
  <div class="input-group mb-2">
    <select class="form-select" v-model="selected">
      <option selected :value="undefined">-- {{ placeholder }} --</option>
      <option v-for="[k, o] of options" :value="k">{{ o }}</option>
    </select>
  </div>
</template>
