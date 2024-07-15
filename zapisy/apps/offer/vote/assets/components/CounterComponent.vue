<script setup lang="ts">
import { sum, values } from "lodash";
import { computed } from "vue";
// The component displaying the message will get two inputs. One is a point
// limit, the other is a map of point values from input fields, keyed by the
// input id.
const props = defineProps<{
  inputs: { [key: string]: number };
  limit: number;
}>();

const total = computed(() => sum(values(props.inputs)));
const exceedsLimit = computed(() => total.value > props.limit);
</script>

<template>
  <div class="alert alert-info" :class="{ 'alert-danger': exceedsLimit }">
    Wykorzystano {{ total }} z {{ limit }} punktów
  </div>
</template>
