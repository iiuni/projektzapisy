<script lang="ts">
import { isEmpty, property } from "lodash";
import { defineComponent } from "vue";
import { mapMutations } from "vuex";
import Multiselect from "vue-multiselect";
import "./MultiSelectFilter.scss";

import { Filter } from "@/enrollment/timetable/assets/store/filters";
import { MultiselectFilterData, MultiselectFilterDataItem } from "../../models";

class ExactFilter implements Filter {
  constructor(
    public ids: Array<string | number>,
    public propertyName: string
  ) {}
  visible(c: Object): boolean {
    if (isEmpty(this.ids)) {
      return true;
    }
    let propGetter = property(this.propertyName) as (c: Object) => string;
    let propValue = propGetter(c);
    return this.ids.includes(propValue);
  }
}

const isDefinedOption = (
  option: undefined | MultiselectFilterDataItem<number | string>
): option is MultiselectFilterDataItem<number | string> =>
  option !== undefined &&
  "value" in option &&
  (typeof option.value === "string" || typeof option.value === "number");

type Props = {
  property: string;
  filterKey: string;
  options: MultiselectFilterData<string | number>;
  placeholder: string;
  showLabels?: boolean;
  trackBy?: string;
  propAsLabel?: string;
};

type Data = {
  selected: MultiselectFilterData<string | number>;
};

type Computed = {
  selectedValue: () => string;
};

type Methods = {
  registerFilter: Function;
  clearFilter: () => void;
  clearAll: () => void;
  updateDropdownWidth: () => void;
};

export default defineComponent<Props, any, Data, Computed, Methods>({
  components: { Multiselect },
  props: {
    property: String,
    filterKey: String,
    options: Array as () => MultiselectFilterData<string | number>,
    placeholder: String,
    showLabels: {
      type: Boolean,
      default: false,
    },
    trackBy: {
      type: String,
      default: "value",
    },
    propAsLabel: {
      type: String,
      default: "label",
    },
  },
  data() {
    return {
      selected: [] as Array<{ value: number; label: string }>,
    };
  },
  created: function () {
    const searchParams = new URL(window.location.href).searchParams;
    if (searchParams.has(this.property)) {
      const property = searchParams.get(this.property);
      if (property && property.length) {
        const ids = searchParams.get(this.property)!.split(",");
        this.selected = ids
          .map((id) =>
            this.options.find(
              (option: { value: number; label: string }) =>
                String(option.value) == id
            )
          )
          .filter((option) => isDefinedOption(option));
      }
    }

    this.$store.subscribe((mutation: { type: string }) => {
      switch (mutation.type) {
        case "filters/clearFilters":
          this.selected = [];
          break;
      }
    });
  },
  mounted() {
    this.updateDropdownWidth();

    window.addEventListener("resize", this.updateDropdownWidth);
  },
  unmounted() {
    window.removeEventListener("resize", this.updateDropdownWidth);
  },
  methods: {
    ...mapMutations("filters", ["registerFilter"]),
    clearFilter() {
      this.selected = [];
    },
    clearAll() {
      this.selected = [];
    },
    updateDropdownWidth() {
      const multiselectInputs =
        document.querySelectorAll<HTMLElement>(".multiselect");

      Array.from(multiselectInputs).forEach((multiselectInput) => {
        const dropdown = multiselectInput.querySelectorAll<HTMLElement>(
          ".multiselect__content-wrapper"
        )[0];

        if (dropdown) {
          dropdown.style.width = `${multiselectInput.offsetWidth}px`;
        }
      });
    },
  },
  computed: {
    selectedValue(): string {
      return this.selected
        .map(({ label }: { label: string }) => label)
        .join(", ");
    },
  },
  watch: {
    selected: function () {
      const selectedIds = this.selected.map(
        (selectedFilter: MultiselectFilterDataItem<number | string>) =>
          selectedFilter.value
      );

      const url = new URL(window.location.href);
      if (isEmpty(selectedIds)) {
        url.searchParams.delete(this.property);
      } else {
        url.searchParams.set(this.property, selectedIds.join(","));
      }
      window.history.replaceState(null, "", url.toString());

      this.registerFilter({
        k: this.filterKey,
        f: new ExactFilter(selectedIds, this.property),
      });
    },
  },
});
</script>

<template>
  <div class="mb-2">
    <multiselect
      v-model="selected"
      :options="options"
      :show-labels="showLabels"
      :multiple="true"
      :close-on-select="false"
      :track-by="trackBy"
      :label="propAsLabel"
      :placeholder="placeholder"
    >
      <template slot="option" slot-scope="props">
        <div class="option-row">
          <div class="custom-control custom-checkbox">
            <input
              type="checkbox"
              class="custom-control-input"
              :checked="selected.includes(props.option)"
            />
            <label class="custom-control-label" :for="filterKey"></label>
          </div>
          {{ props.option.label }}
        </div>
      </template>
      <template slot="selection" slot-scope="{ values, isOpen }">
        <span class="multiselect__single" v-if="values.length" v-show="!isOpen">
          {{ selectedValue }}
        </span>
      </template>
      <template slot="clear">
        <div
          v-show="selected.length"
          class="multiselect__clear"
          @mousedown.prevent.stop="clearAll"
        >
          ×
        </div>
      </template>
    </multiselect>
  </div>
</template>

<style>
.option-row {
  font-size: 12px;
  display: flex;
  flex-direction: row;
  align-items: center;
}

.checkbox-placeholder {
  margin-right: 12px;
}
</style>
