<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import { ThesisInfo } from "../store/theses";
import SorterField from "./sorters/SorterField.vue";
import Component from "vue-class-component";

@Component({
  components: {
    SorterField,
  },
  computed: {
    ...mapGetters("theses", {
      theses: "theses",
    }),
    ...mapGetters("filters", {
      tester: "visible",
    }),
    ...mapGetters("sorting", {
      compare: "compare",
    }),
  },
})
export default class ThesesList extends Vue {
  // The list should be initialised to contain all the theses and then apply
  // filters and sorting whenever they update.
  visibleTheses: ThesisInfo[] = [];

  theses!: ThesisInfo[];
  tester!: (_: ThesisInfo) => boolean;
  compare!: (a: ThesisInfo, b: ThesisInfo) => number;

  created() {
    this.$store.dispatch("theses/initFromJSONTag");
  }

  mounted() {
    this.visibleTheses = this.theses.sort(this.compare);

    this.$store.subscribe((mutation, state) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleTheses = this.theses.filter(this.tester);
          this.visibleTheses.sort(this.compare);
          break;
        case "sorting/changeSorting":
          this.visibleTheses = this.theses.filter(this.tester);
          this.visibleTheses.sort(this.compare);
          break;
      }
    });
  }

  reservedUntilAltText(thesis: ThesisInfo): string | undefined {
    if (!thesis.reserved_until) {
      return undefined;
    }
    return `Zarezerwowana do ${thesis.reserved_until}`;
  }
}
</script>

<template>
  <table class="table table-hover table-responsive-md">
    <thead id="table-header">
      <tr class="text-center">
        <th>
          <SorterField property="title" label="Tytuł" />
        </th>
        <th>
          <SorterField property="kind" label="Typ" />
        </th>
        <th>
          <SorterField property="advisor_last_name" label="Promotor" />
        </th>
        <th>Rezerwacja</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="thesis of visibleTheses" :key="thesis.id">
        <td class="align-middle">
          <a class="btn-link" :href="thesis.url">{{ thesis.title }}</a>
          <em v-if="thesis.status !== 'zaakceptowana'" class="text-muted"
            >({{ thesis.status }})</em
          >
        </td>
        <td class="text-center align-middle">
          {{ thesis.kind }}
        </td>
        <td class="align-middle">
          {{ thesis.advisor }}
        </td>
        <td
          class="align-middle"
          :class="{ 'text-muted': thesis.is_available }"
          :title="reservedUntilAltText(thesis)"
        >
          {{ thesis.students }}
        </td>
      </tr>
      <tr v-if="!visibleTheses.length" class="text-center">
        <td colspan="4">
          <em class="text-muted">Brak prac dyplomowych.</em>
        </td>
      </tr>
    </tbody>
  </table>
</template>
