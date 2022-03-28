<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import { DefectInfo } from "@/defect/assets/models";
import SorterField from "@/theses/assets/components/sorters/SorterField.vue";
import Component from "vue-class-component";

@Component({
  components: {
    SorterField,
  },
  computed: {
    ...mapGetters("defects", {
      defects: "defects",
    }),
    ...mapGetters("filters", {
      tester: "visible",
    }),
    ...mapGetters("sorting", {
      compare: "compare",
      isEmpty: "isEmpty",
    }),
  },
})
export default class DefectList extends Vue {
  // The list should be initialised to contain all the defects and then apply
  // filters and sorting whenever they update.
  visibleDefects: DefectInfo[] = [];

  defects!: DefectInfo[];
  tester!: (_: DefectInfo) => boolean;
  compare!: (a: DefectInfo, b: DefectInfo) => number;

  created() {
    this.$store.dispatch("defects/initFromJSONTag");
  }

  mounted() {
    this.visibleDefects = this.defects;
    this.visibleDefects = this.defects.sort(this.compare);

    this.$store.subscribe((mutation, state) => {
      switch (mutation.type) {
        case "filters/registerFilter":
        case "sorting/changeSorting":
          this.visibleDefects = this.defects.filter(this.tester);
          this.visibleDefects.sort(this.compare);
          break;
      }
    });
  }

  // @ts-ignore
  select(event) {
    // @ts-ignore
    if (!event.currentTarget.classList.contains("selected"))
      // @ts-ignore
      event.currentTarget.classList.add("selected");
    // @ts-ignore
    else event.currentTarget.classList.remove("selected");
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
.selected {
  background-color: #c2dbff !important;
}
</style>

<template>
  <table class="table table-hover selection-none table-responsive-md">
    <thead id="table-header">
      <tr class="text-center" id="headers">
        <th>
          <SorterField property="name" label="Nazwa Usterki" />
        </th>
        <th>
          <SorterField property="place" label="Miejsce usterki" />
        </th>
        <th>
          <SorterField property="state" label="Stan Usterki" />
        </th>
        <th>
          <SorterField property="creation_date" label="Data zgłoszenia" />
        </th>
        <th>
          <SorterField property="last_modification" label="Data modyfikacji" />
        </th>
      </tr>
    </thead>
    <tbody>
      <tr
        v-on:click="select"
        v-for="defect of visibleDefects"
        :key="defect.id"
        :id="defect.id"
      >
        <td class="text-center align-middle">
          <a class="btn-link" :href="'/defect/' + defect.id">{{
            defect.name
          }}</a>
        </td>
        <td class="text-center align-middle">
          {{ defect.place }}
        </td>
        <td class="text-center align-middle" :style="defect.status_color">
          {{ defect.state }}
        </td>
        <td class="text-center">
          {{ defect.creation_date }}
        </td>
        <td class="text-center">
          {{ defect.last_modification }}
        </td>
      </tr>
      <tr v-if="!visibleDefects.length" class="text-center">
        <td colspan="5">
          <em class="text-muted">Brak widocznych usterek.</em>
        </td>
      </tr>
    </tbody>
  </table>
</template>
