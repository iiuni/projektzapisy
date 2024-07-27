<script setup lang="ts">
import { computed, ref } from "vue";
import emitter from "tiny-emitter/instance";
import { sortBy, some, every, map, get, filter } from "lodash";
import { onBeforeMount } from "vue";
import { onMounted } from "vue";

// TODO Refactor emitter
// TODO add types for user

const filter_phrase = ref("");
const filter_button = ref("");
const users = ref([]);
const userLinkUrl = ref("");

onBeforeMount(() => {
  let rawUsers = JSON.parse(
    document.getElementById("user-list-json-script")!.textContent!
  );
  users.value = Object.values(rawUsers);
  users.value = sortBy(users.value, ["last_name", "first_name"]);
  userLinkUrl.value = document
    .getElementById("user-link")!
    .getAttribute("data")!;
});

onMounted(() => {
  emitter.on("user-char-filter", (value) => {
    filter_button.value = value;
  });
  emitter.on("user-input-filter", (value) => {
    filter_phrase.value = value;
  });
});

const matchedUsers = computed(() => {
  return filter(users.value, (user) => matchChar(user) && matchInput(user));
});

const matchInput = (user) => {
  // Remove trailing/leading whitespaces from input
  let phrase = filter_phrase.value.toLowerCase().trim();
  const regex = /\s+/;
  let words = phrase.split(regex);

  const props = ["first_name", "last_name", "email", "album"];
  const values = map(props, (p) => get(user, p, "").toLowerCase());
  const anyPropMatches = (word) => some(values, (v) => v.includes(word));
  return every(words, anyPropMatches);
};

const matchChar = (user) => {
  let last_name = user.last_name.toLowerCase();
  let button = filter_button.value.toLowerCase();

  if (button != "wszyscy") {
    return last_name.startsWith(button);
  }
  return true;
};
</script>

<template>
  <ul>
    <li v-for="user in matchedUsers" :key="user.id" class="mb-1">
      <a :href="userLinkUrl + user.id"
        >{{ user.first_name }} {{ user.last_name }}</a
      >
    </li>
  </ul>
</template>
