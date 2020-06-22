<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import { ThesisInfo } from "../store/theses";
import SorterField from "./sorters/SorterField.vue";
import Component from "vue-class-component";

@Component({
  components: {
    SorterField
  },
  computed: {
    ...mapGetters("theses", {
      theses: "theses"
    }),
    ...mapGetters("filters", {
      tester: "visible"
    }),
    ...mapGetters("sorting", {
      compare: "compare",
      isEmpty: "isEmpty"
    })
  }
})
export default class ThesesList extends Vue {
  // The list should be initialised to contain all the theses and then apply
  // filters and sorting whenever they update.
  visibleTheses: ThesisInfo[] = [];

  created() {
    this.$store.dispatch("theses/initFromJSONTag");
  }

  mounted() {
    this.visibleTheses = this.theses;
    this.visibleTheses = this.theses.sort(this.compare);

    this.$store.subscribe((mutation, state) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.visibleTheses = this.theses.filter(
            this.tester
          );
          this.visibleTheses.sort(this.compare);
          break;
        case "sorting/changeSorting":
          this.visibleTheses = this.theses.filter(
            this.tester
          );
          this.visibleTheses.sort(this.compare);
          break;
      }
    });
  }
}
</script>

<style scoped>
.selection-none {
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  user-select: none;
}
</style>

<template>
  <table class="table table-hover selection-none">
    <thead id="table-header">
      <tr class="text-center">
        <th>
          <SorterField property="title" label="Tytuł" />
        </th>
        <th>
          <SorterField property="kind" label="Typ" />
        </th>
        <th>
          <SorterField
            property="advisor_last_name"
            label="Promotor"
          />
        </th>
        <th>Rezerwacja</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="t of visibleTheses" :key="t.id">
        <td class="align-middle">
          <a class="btn-link" :href="t.url">{{
            t.title
          }}</a>
          <em v-if="!t.has_been_accepted" class="text-muted"
            >({{ t.status }})</em
          >
        </td>
        <td class="text-center align-middle">
          {{ t.kind }}
        </td>
        <td class="align-middle text-nowrap">
          {{ t.advisor }}
        </td>
        <td class="align-middle" :class="{'text-muted': t.is_available}">
          {{ t.students }}
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
