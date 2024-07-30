<script setup lang="ts">
import { computed, onMounted } from "vue";
import { ref } from "vue";
import { useStore } from "vuex";
const store = useStore();

// TODO unify defineProps
const props = defineProps<{
  property: string;
  label: string;
}>();

const order = ref(0);
onMounted(() => {
  store.subscribe((mutation) => {
    switch (mutation.type) {
      case "sorting/changeSorting":
        if (getSortingProperty.value != props.property) order.value = 0;
        break;
    }
  });
});
const getSortingProperty = computed(() => {
  return store.getters["sorting/getProperty"];
});

const changeSorting = ({ k, f }) => {
  store.commit("sorting/changeSorting", { k, f });
};
const sort = () => {
  if (order.value == 2) {
    changeSorting({
      k: "modified",
      f: false,
    });
    order.value = 0;
  } else {
    changeSorting({
      k: props.property,
      f: order.value === 0,
    });
    order.value += 1;
  }
};
</script>

<template>
  <div style="cursor: pointer" v-on:click="sort()">
    {{ label }}
    <span v-if="order == 1">&darr;</span>
    <span v-if="order == 2">&uarr;</span>
  </div>
</template>
