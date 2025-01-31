<script lang="ts">
import { isEmpty, property } from "lodash";
import { defineComponent } from "vue";
import { mapMutations } from "vuex";
import Multiselect from "vue-multiselect";

import {
  Filter,
  getSearchParams,
  LAST_FILTER_KEY,
} from "@/enrollment/timetable/assets/store/filters";
import { MultiselectFilterDataItem } from "../../models";

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

const isDefinedOption = (option: undefined | Option): option is Option =>
  option !== undefined &&
  "value" in option &&
  (typeof option.value === "string" || typeof option.value === "number");

type Props = {
  property: string;
  filterKey: string;
  options: Options;
  placeholder: string;
  showLabels?: boolean;
  trackBy?: string;
  propAsLabel?: string;
};

type Options = Option[];
type Option = MultiselectFilterDataItem<string | number>;

type Data = {
  selected: Options;
};

type Computed = {
  selectionDescription: () => string;
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
    options: Array as () => Options,
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
    // Which CourseFilter component is it used on
    appID: String,
  },
  data() {
    return {
      selected: [] as Options,
    };
  },
  created: function () {
    const searchParams = getSearchParams();
    if (searchParams.has(this.appID + "_" + this.property)) {
      const property = searchParams.get(this.appID + "_" + this.property);
      if (property && property.length) {
        const ids = searchParams
          .get(this.appID + "_" + this.property)!
          .split(",");

        this.selected = ids
          .map((id) =>
            this.options.find((option: Option) => String(option.value) == id)
          )
          .filter((el) => isDefinedOption(el)) as Options;
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
    selectionDescription(): string {
      if (this.selected.length === 0) {
        return this.placeholder;
      }
      return this.options
        .filter((opt) => this.selected.includes(opt))
        .map(({ label }: { label: string }) => label)
        .join(", ");
    },
  },
  watch: {
    selected: function () {
      const selectedIds = this.selected.map(
        (selectedFilter: Option) => selectedFilter.value
      );

      const searchParams = getSearchParams();
      if (isEmpty(selectedIds)) {
        searchParams.delete(this.appID + "_" + this.property);
        sessionStorage.removeItem(LAST_FILTER_KEY);
        if (searchParams.toString().length != 0) {
          sessionStorage.setItem(LAST_FILTER_KEY, searchParams.toString());
        }
      } else {
        searchParams.set(
          this.appID + "_" + this.property,
          selectedIds.join(",")
        );
        sessionStorage.setItem(LAST_FILTER_KEY, searchParams.toString());
      }

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
      :placeholder="selectionDescription"
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
          {{ selectionDescription }}
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

<style lang="scss" scoped>
@import "~vue-multiselect/dist/vue-multiselect.min.css";
</style>

<style lang="scss">
.multiselect__clear {
  position: absolute;
  right: 34px;
  height: 100%;
  width: 40px;
  cursor: pointer;
  z-index: 2;
  display: flex;
  justify-content: center;
  align-items: center;
}

.multiselect,
.multiselect__input,
.multiselect__single {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.multiselect {
  display: table;
  table-layout: fixed;
  min-height: unset;
}

/* We intentionally disable transforming this element to enable it on
the ::before pseudo-element below.
This is needed because the "actual" element has border now,
and its rotating is unaestheticly baroque.
Instead, we only want the inner arrow to rotate. */
.multiselect--active .multiselect__select {
  transform: none;
}

.multiselect--active .multiselect__select::before {
  transform: rotateZ(180deg);
}

.multiselect__input,
.multiselect__single {
  padding: unset;
  margin-bottom: unset;
}

.multiselect__tags {
  min-height: calc(1.5em + 0.75rem + 2px);
  padding: 0.375rem 4rem 0.375rem 0.75rem;
}

.multiselect__select {
  line-height: unset;
  width: unset;
  height: unset;
  right: 0px;
  top: 0px;
  padding: 0.375rem 0.75rem;
  background: rgb(248, 249, 250);
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-top-right-radius: 5px;
  border-bottom-right-radius: 5px;
  border: 1px solid #6c757d;
}

.multiselect__select::before {
  display: inline-block;
  top: 18%;
}

.multiselect__placeholder {
  height: 20px;
  font-size: 0.9rem;
  margin-bottom: unset;
  padding-top: unset;
}

.multiselect__content-wrapper {
  /* Other positions either make the options list totally invisible,
  or prevent it from sticking out of the filters card (in other words,
  when the list is expanded, but the card is not, the list is cut). */
  position: fixed;
}

.multiselect__option--highlight,
.multiselect__option--selected.multiselect__option--highlight,
.multiselect__option--selected.multiselect__option--highlight::after {
  background: rgb(234, 236, 239);
  color: unset;
}

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
