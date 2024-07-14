<script setup lang="ts">
import SimpleTimetable from "./SimpleTimetable.vue";
import PrototypeDay from "./PrototypeDay.vue";
</script>

<template>
  <SimpleTimetable v-bind="$attrs">
    <template #day="{ d, terms }">
      <PrototypeDay :d="d" :terms="terms" />
    </template>
  </SimpleTimetable>
</template>
