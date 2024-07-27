<script setup lang="ts">
import { ref } from "vue";
import emitter from "tiny-emitter/instance";

const input_value = ref("");
const selectedChar = ref("Wszyscy");
// prettier-ignore
const chars = ["A", "B", "C", "Ć", "D", "E", "F", "G", "H", "I", "J", "K", "L",
              "Ł", "M", "N", "Ń", "O", "Q", "P", "R", "S", "Ś", "T", "U", "W",
              "X", "Y", "Z", "Ż", "Ź", "Wszyscy"];

const emitInputFilter = (event) => {
  input_value.value = event.target.value;
  emitter.emit("user-input-filter", event.target.value);
};
const emitCharFilter = (char) => {
  selectedChar.value = char;
  emitter.emit("user-char-filter", char);
};
</script>

<template>
  <div class="card bg-light">
    <div class="card-body">
      <input
        class="form-control"
        type="text"
        :value="input_value"
        @input="emitInputFilter"
        placeholder="Filtrowanie"
      />
      <hr />
      <button
        v-for="char in chars"
        :key="char"
        class="btn btn-link p-1"
        v-on:click="emitCharFilter(char)"
        :class="{ 'text-dark': selectedChar === char }"
      >
        {{ char }}
      </button>
    </div>
  </div>
</template>
