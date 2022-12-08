<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";
import { DefectInfo } from "@/defects/assets/models";
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
          this.set_forms_values();
        case "sorting/changeSorting":
          this.visibleDefects = this.defects.filter(this.tester);
          this.visibleDefects.sort(this.compare);
          break;
      }
    });
  }

  set_forms_values() {
    // @ts-ignore
    let selected = Array.prototype.map
      .call(document.getElementsByClassName("selected"), function (x) {
        return x.id;
      })
      .join(",");
    // @ts-ignore
    document.getElementById("defects_ids_print").value = selected;
    // @ts-ignore
    let delete_button = document.getElementById("defects_ids_delete");
    // @ts-ignore
    if (delete_button) delete_button.value = selected;
  }

  // @ts-ignore
  select(event) {
    // @ts-ignore
    !event.currentTarget.classList.toggle("selected");
    let selected_defects = document.getElementsByClassName("selected");
    let print_button = document.getElementById("print-button")!;
    if (selected_defects.length > 0) {
      let link = "print/";
      let selected_ids = Array.prototype.map
        .call(selected_defects, (x) => {
          return x.id;
        })
        .join(",");
      print_button.textContent = "Drukuj zaznaczone";
      print_button.setAttribute("href", link + selected_ids);
      // @ts-ignore
      let delete_button = document.getElementById("delete-form-button");
      if (delete_button)
        // @ts-ignore
        document.getElementById("delete-form-button").disabled = false;
    } else {
      print_button.textContent = "Drukuj wszystkie";
      print_button.setAttribute("href", "print");
      // @ts-ignore
      let delete_button = document.getElementById("delete-form-button");
      if (delete_button)
        // @ts-ignore
        document.getElementById("delete-form-button").disabled = true;
    }
    this.set_forms_values();
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
          <SorterField property="name" label="Nazwa" />
        </th>
        <th>
          <SorterField property="place" label="Miejsce" />
        </th>
        <th>
          <SorterField property="reporter" label="Zgłoszona przez" />
        </th>
        <th>
          <SorterField property="state" label="Stan" />
        </th>
        <th>
          <SorterField property="creation_date" label="Data zgłoszenia" />
        </th>
        <th>
          <SorterField property="last_modification" label="Data modyfikacji" />
        </th>
      </tr>
    </thead>
    <tbody id="defects-table-body">
      <tr v-on:click="select" v-for="defect of visibleDefects" :key="defect.id" :id="defect.id">
        <td class="text-center align-middle">
          <a class="btn-link" :href="'/defects/' + defect.id">{{
              defect.name
          }}</a>
        </td>
        <td class="text-center align-middle">
          {{ defect.place }}
        </td>
        <td class="text-center align-middle">
          {{ defect.reporter }}
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
        <td colspan="6">
          <em class="text-muted">Brak widocznych usterek.</em>
        </td>
      </tr>
    </tbody>
  </table>
</template>
