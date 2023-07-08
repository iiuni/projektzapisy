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
          this.visibleDefects = this.defects.filter(this.tester);
          this.visibleDefects.sort(this.compare);
          this.deselect_hidden_defects();
          this.set_forms_values();
          break;
        case "sorting/changeSorting":
          this.visibleDefects = this.defects.filter(this.tester);
          this.visibleDefects.sort(this.compare);
          this.set_forms_values();
          break;
      }
    });

    let print_button = document.getElementById("print-button")!;
    let delete_button = document.getElementById(
      "delete-form-button"
    )! as HTMLButtonElement;

    delete_button.onclick = () => {
      let selected = this.visibleDefects
        .filter((x) => x.selected)
        .map((x) => x.id);
      let defect_ids_delete = document.getElementById(
        "defects_ids_delete"
      )! as HTMLButtonElement;

      defect_ids_delete.value = selected.join(",");
      return confirm(generate_delete_message_for_n_defects(selected.length));
    };

    print_button.onclick = () => {
      let link = "print/";

      if (this.visibleDefects.some((x) => x.selected)) {
        let selected = this.visibleDefects
          .filter((x) => x.selected)
          .map((x) => x.id)
          .join(",");

        print_button.setAttribute("href", link + selected);
      } else {
        let visible_defects = this.visibleDefects.map((x) => x.id).join(",");
        print_button.setAttribute("href", link + visible_defects);
      }
    };
  }

  set_forms_values() {
    let delete_button = document.getElementById(
      "delete-form-button"
    )! as HTMLButtonElement;
    let print_button = document.getElementById("print-button")!;

    if (this.visibleDefects.some((x) => x.selected)) {
      print_button.textContent = "Drukuj zaznaczone";

      delete_button.disabled = false;
    } else {
      if (this.defects.length - this.visibleDefects.length > 0)
        print_button.textContent = "Drukuj widoczne";
      else print_button.textContent = "Drukuj wszystkie";
      delete_button.disabled = true;
    }
  }

  select(event: PointerEvent) {
    let defectTable = event.currentTarget! as HTMLTableElement;
    let isSelected = defectTable.classList.toggle("selected");
    let checkboxForSelectedRow = document.getElementById(
      "checkbox-" + defectTable.id
    )! as HTMLInputElement;
    this.defects.find((x) => x.id == Number(defectTable.id))!.selected =
      isSelected;
    checkboxForSelectedRow.checked = isSelected;
    this.set_forms_values();
  }

  deselect_hidden_defects() {
    let defectsToDeselect = this.defects.filter(
      (x) => x.selected && !this.visibleDefects.includes(x)
    );
    defectsToDeselect.forEach((x) => (x.selected = false));
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
