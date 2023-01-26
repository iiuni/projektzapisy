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
  // The list should be initialized to contain all the defects and then apply
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
          break;
        case "sorting/changeSorting":
          this.visibleDefects = this.defects.filter(this.tester);
          this.visibleDefects.sort(this.compare);
          break;
      }
    });
  }

  set_forms_values() {
    let selected = Array.from(document.getElementsByClassName("selected")).map(
      (x) => x.id
    );
    let selected_str_rep = selected.join(",");
    let defects_ids_print = document.getElementById(
      "defects_ids_print"
    )! as HTMLInputElement;
    defects_ids_print.value = selected_str_rep;
    let defect_ids_delete = document.getElementById(
      "defects_ids_delete"
    )! as HTMLButtonElement;
    if (defect_ids_delete) defect_ids_delete.value = selected_str_rep;
    let delete_button = document.getElementById(
      "delete-form-button"
    )! as HTMLButtonElement;
    if (delete_button)
      delete_button.onclick = function () {
        return confirm(generate_delete_message_for_n_defects(selected.length));
      };
  }

  select(event: PointerEvent) {
    let defectTable = event.currentTarget! as HTMLTableElement;
    let isSelected = defectTable.classList.toggle("selected");
    let checkboxForSelectedRow = document.getElementById(
      "checkbox-" + defectTable.id
    )! as HTMLInputElement;
    checkboxForSelectedRow.checked = isSelected;
    let selected_defects = document.getElementsByClassName("selected");
    let print_button = document.getElementById("print-button")!;
    if (selected_defects.length > 0) {
      let link = "print/";
      let selected_ids = Array.from(selected_defects)
        .map((x) => x.id)
        .join(",");
      print_button.textContent = "Drukuj zaznaczone";
      print_button.setAttribute("href", link + selected_ids);
      let delete_button = document.getElementById(
        "delete-form-button"
      ) as HTMLButtonElement;
      if (delete_button) delete_button.disabled = false;
    } else {
      print_button.textContent = "Drukuj wszystkie";
      print_button.setAttribute("href", "print");
      let delete_button = document.getElementById(
        "delete-form-button"
      )! as HTMLButtonElement;
      if (delete_button) delete_button.disabled = true;
    }
    this.set_forms_values();
  }
}
function generate_delete_message_for_n_defects(n: number) {
  //https://rjp.pan.pl/porady-jezykowe-main/1011-skadnia-liczebnikow-70
  if (n == 1) {
    return "Czy na pewno chcesz usunąć 1 usterkę?";
  } else if (n % 10 >= 2 && n % 10 <= 4 && (n % 100 < 10 || n % 100 > 20)) {
    return "Czy na pewno chcesz usunąć " + n + " usterki?";
  } else {
    return "Czy na pewno chcesz usunąć " + n + " usterek?";
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
        <th></th>
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
      <tr
        v-on:click="select"
        v-for="defect of visibleDefects"
        :key="defect.id"
        :id="defect.id"
      >
        <td>
          <input
            type="checkbox"
            :id="'checkbox-' + defect.id"
            autocomplete="off"
          />
        </td>
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
        <td colspan="7">
          <em class="text-muted">Brak widocznych usterek.</em>
        </td>
      </tr>
    </tbody>
  </table>
</template>
