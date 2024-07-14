<script setup lang="ts">
import Day from "./Day.vue";
import TermControls from "./TermControls.vue";
</script>

<template>
  <Day v-bind="$attrs" v-on="$listeners">
    <template #default="{ term }">
      <TermControls :term="term" />
    </template>
  </Day>
</template>
