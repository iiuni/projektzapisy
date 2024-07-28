<script setup lang="ts">
import { ref, watch } from "vue";
import { property } from "lodash";
import { ThesisInfo } from "../../store/theses";
import { Filter } from "../../store/filters";
import { useStore } from "vuex";
const store = useStore();

class TextFilter implements Filter {
  propGetters: ((c: ThesisInfo) => string)[];

  constructor(public pattern: string = "", public propertyNames: string[]) {
    this.propGetters = this.propertyNames.map((propName) => property(propName));
  }

  visible(c: ThesisInfo): boolean {
    const patternWords = this.pattern.toLocaleLowerCase().split(" ");
    const propValues = this.propGetters.map((f) => f(c).toLocaleLowerCase());
    const patternWordMatches = patternWords.map((w) =>
      propValues.some((v) => v.includes(w))
    );
    return patternWordMatches.every((b) => b);
  }
}

const props = defineProps<{
  properties: string[];
  filterKey: string;
  placeholder: string;
}>();
const pattern = ref("");

watch(pattern, (newPattern) => {
  store.commit("filters/registerFilter", {
    k: props.filterKey,
    f: new TextFilter(newPattern, props.properties),
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
