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

<script lang="ts">
import { isEmpty, property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";
import Multiselect from "vue-multiselect";

import { Filter } from "@/enrollment/timetable/assets/store/filters";

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

interface Option {
  value: number;
  label: string;
}
const isDefinedOption = (
  option: undefined | { value: number; label: string }
): option is Option => option !== undefined && "value" in option;

export default Vue.extend({
  components: { Multiselect },
  props: {
    property: String,
    filterKey: String,
    options: Array as () => Array<{ value: number; label: string }>,
    title: String,
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
            this.options.find((option) => String(option.value) == id)
          )
          .filter((option) => isDefinedOption(option)) as Option[];
      }
    }

    this.$store.subscribe((mutation, _) => {
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
      const multiselectInputs = document.getElementsByClassName("multiselect");

      Array.from(multiselectInputs).forEach((multiselectInput, index) => {
        const dropdown = document.getElementsByClassName(
          "multiselect__content-wrapper"
        )[index];

        if (dropdown) {
          dropdown.style.width = `${multiselectInput.offsetWidth}px`;
        }
      });
    },
  },
  computed: {
    selectedValue() {
      const result: string[] = [];
      let length = 0;

      this.selected.every((value: { label: string }) => {
        if (length + value.label.length < 25) {
          length += value.label.length;
          result.push(value.label);
          return value;
        }
      });

      const otherOptions: number = this.selected.length - result.length;
      const word =
        otherOptions > 4 ? "innych" : otherOptions > 1 ? "inne" : "inny";
      return `${result.join(", ")}${
        otherOptions > 0 ? ` + ${otherOptions} ${word}` : ""
      }`;
    },
  },
  watch: {
    selected: function () {
      const selectedIds = this.selected.map(
        (selectedFilter: { value: number; label: string }) =>
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

<style>
fieldset[disabled] .multiselect {
  pointer-events: none;
}
.multiselect__spinner {
  position: absolute;
  right: 1px;
  top: 1px;
  width: 40px;
  height: 38px;
  background: #fff;
  display: block;
}

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

.multiselect__spinner:before,
.multiselect__spinner:after {
  position: absolute;
  content: "";
  top: 50%;
  left: 50%;
  margin: -8px 0 0 -8px;
  width: 16px;
  height: 16px;
  border-radius: 100%;
  border-color: #41b883 transparent transparent;
  border-style: solid;
  border-width: 2px;
  box-shadow: 0 0 0 1px transparent;
  display: inline-block;
}
.multiselect__spinner:before {
  animation: spinning 2.4s cubic-bezier(0.41, 0.26, 0.2, 0.62);
  animation-iteration-count: infinite;
}
.multiselect__spinner:after {
  animation: spinning 2.4s cubic-bezier(0.51, 0.09, 0.21, 0.8);
  animation-iteration-count: infinite;
}
.multiselect__loading-enter-active,
.multiselect__loading-leave-active {
  transition: opacity 0.4s ease-in-out;
  opacity: 1;
}
.multiselect__loading-enter,
.multiselect__loading-leave-active {
  opacity: 0;
}
.multiselect,
.multiselect__input,
.multiselect__single {
  font-family: inherit;
  font-size: 0.9rem;
  touch-action: manipulation;
}
.multiselect {
  box-sizing: content-box;
  display: block;
  position: relative;
  width: 100%;
  text-align: left;
  color: #35495e;
}
.multiselect * {
  box-sizing: border-box;
}
.multiselect:focus {
  outline: none;
}
.multiselect--disabled {
  background: #ededed;
  pointer-events: none;
  opacity: 0.6;
}
.multiselect--active {
  z-index: 50;
}
.multiselect--active:not(.multiselect--above) .multiselect__current,
.multiselect--active:not(.multiselect--above) .multiselect__input,
.multiselect--active:not(.multiselect--above) .multiselect__tags {
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
}
.multiselect--active .multiselect__select:before {
  transform: rotateZ(180deg);
}
.multiselect--above.multiselect--active .multiselect__current,
.multiselect--above.multiselect--active .multiselect__input,
.multiselect--above.multiselect--active .multiselect__tags {
  border-top-left-radius: 0;
  border-top-right-radius: 0;
}
.multiselect__input {
  padding: 0;
}

.multiselect__input,
.multiselect__single {
  position: relative;
  display: inline-block;
  min-height: 20px;
  line-height: 20px;
  border: none;
  border-radius: 5px;
  background: #fff;
  width: calc(100%);
  transition: border 0.1s ease;
  box-sizing: border-box;
  vertical-align: top;
}
.multiselect__input::placeholder {
  color: #35495e;
}
.multiselect__tag ~ .multiselect__input,
.multiselect__tag ~ .multiselect__single {
  width: auto;
}
.multiselect__input:hover,
.multiselect__single:hover {
  border-color: #cfcfcf;
}
.multiselect__input:focus,
.multiselect__single:focus {
  border-color: #a8a8a8;
  outline: none;
}
.multiselect__single {
  /*padding-left: 5px;*/
  /*margin-bottom: 8px;*/
}
.multiselect__tags-wrap {
  display: inline;
}
.multiselect__tags {
  min-height: calc(1.5em + 0.75rem + 2px);
  padding: 0.375rem 40px 0.375rem 0.75rem;
  display: block;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
  background: #fff;
  font-size: 14px;
}
.multiselect__tag {
  position: relative;
  display: inline-block;
  padding: 4px 26px 4px 10px;
  border-radius: 5px;
  margin-right: 10px;
  color: #fff;
  line-height: 1;
  background: #41b883;
  margin-bottom: 5px;
  white-space: nowrap;
  overflow: hidden;
  max-width: 100%;
  text-overflow: ellipsis;
}
.multiselect__tag-icon {
  cursor: pointer;
  margin-left: 7px;
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  font-weight: 700;
  font-style: initial;
  width: 22px;
  text-align: center;
  line-height: 22px;
  transition: all 0.2s ease;
  border-radius: 5px;
}
.multiselect__tag-icon:after {
  content: "×";
  color: #266d4d;
  font-size: 14px;
}
.multiselect__tag-icon:focus,
.multiselect__tag-icon:hover {
  background: rgb(234, 236, 239);
}
.multiselect__tag-icon:focus:after,
.multiselect__tag-icon:hover:after {
  color: white;
}
.multiselect__current {
  line-height: 16px;
  box-sizing: border-box;
  display: block;
  overflow: hidden;
  padding: 8px 12px 0;
  padding-right: 30px;
  white-space: nowrap;
  margin: 0;
  text-decoration: none;
  border-radius: 5px;
  border: 1px solid #e8e8e8;
  cursor: pointer;
}
.multiselect__select {
  display: block;
  position: absolute;
  box-sizing: border-box;
  right: 0px;
  top: 0;
  padding: 0.375rem 0.75rem;
  margin: 0;
  text-decoration: none;
  text-align: center;
  cursor: pointer;
  transition: transform 0.2s ease;
  background: rgb(248, 249, 250);
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-top-right-radius: 5px;
  border-bottom-right-radius: 5px;
  border: 1px solid #6c757d;
}
.multiselect__select:before {
  position: relative;
  display: inline-block;
  right: 0;
  top: 18%;
  color: #999;
  margin-top: 4px;
  border-style: solid;
  border-width: 5px 5px 0 5px;
  border-color: #999999 transparent transparent transparent;
  content: "";
}
.multiselect__placeholder {
  color: #adadad;
  display: inline-block;
  height: 20px;
  //font-size: 12px;
  font-size: 0.9rem;
  /*padding-top: 2px;*/
}
.multiselect--active .multiselect__placeholder {
  display: none;
}
.multiselect__content-wrapper {
  position: fixed;
  display: block;
  background: #fff;
  width: 100%;
  max-height: 240px;
  overflow: auto;
  border: 1px solid #e8e8e8;
  border-top: none;
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 5px;
  z-index: 50;
  -webkit-overflow-scrolling: touch;
}
.multiselect__content {
  list-style: none;
  display: inline-block;
  padding: 0;
  margin: 0;
  min-width: 100%;
  vertical-align: top;
}
.multiselect--above .multiselect__content-wrapper {
  bottom: 100%;
  border-bottom-left-radius: 0;
  border-bottom-right-radius: 0;
  border-top-left-radius: 5px;
  border-top-right-radius: 5px;
  border-bottom: none;
  border-top: 1px solid #e8e8e8;
}
.multiselect__content::webkit-scrollbar {
  display: none;
}
.multiselect__element {
  display: block;
}
.multiselect__option {
  display: block;
  padding: 12px;
  line-height: 16px;
  text-decoration: none;
  text-transform: none;
  vertical-align: middle;
  position: relative;
  cursor: pointer;
  white-space: nowrap;
}
.multiselect__option:after {
  top: 0;
  right: 0;
  position: absolute;
  line-height: 40px;
  padding-right: 12px;
  padding-left: 20px;
  font-size: 13px;
}
.multiselect__option--highlight {
  background: rgb(234, 236, 239);
  outline: none;
  /*color: white;*/
}
.multiselect__option--highlight:after {
  content: attr(data-select);
  background: #41b883;
  color: white;
}
.multiselect__option--selected {
  background: #f3f3f3;
  color: #35495e;
  font-weight: bold;
}
.multiselect__option--selected:after {
  content: attr(data-selected);
  color: silver;
  background: inherit;
}
.multiselect__option--selected.multiselect__option--highlight {
  background: rgb(234, 236, 239);
  /*color: #fff;*/
}
.multiselect__option--selected.multiselect__option--highlight:after {
  background: rgb(234, 236, 239);
  content: attr(data-deselect);
  /*color: #fff;*/
}
.multiselect--disabled .multiselect__current,
.multiselect--disabled .multiselect__select {
  background: #ededed;
  color: #a6a6a6;
}
.multiselect__option--disabled {
  background: #ededed !important;
  color: #a6a6a6 !important;
  cursor: text;
  pointer-events: none;
}
.multiselect__option--group {
  background: #ededed;
  color: #35495e;
}
.multiselect__option--group.multiselect__option--highlight {
  background: #35495e;
  color: #fff;
}
.multiselect__option--group.multiselect__option--highlight:after {
  background: #35495e;
}
.multiselect__option--disabled.multiselect__option--highlight {
  background: #dedede;
}
.multiselect__option--group-selected.multiselect__option--highlight {
  background: #ff6a6a;
  color: #fff;
}
.multiselect__option--group-selected.multiselect__option--highlight:after {
  background: #ff6a6a;
  content: attr(data-deselect);
  color: #fff;
}
.multiselect-enter-active,
.multiselect-leave-active {
  transition: all 0.15s ease;
}
.multiselect-enter,
.multiselect-leave-active {
  opacity: 0;
}
.multiselect__strong {
  margin-bottom: 8px;
  line-height: 20px;
  display: inline-block;
  vertical-align: top;
}
*[dir="rtl"] .multiselect {
  text-align: right;
}
*[dir="rtl"] .multiselect__select {
  right: auto;
  left: 1px;
}
*[dir="rtl"] .multiselect__tags {
  padding: 8px 8px 0px 40px;
}
*[dir="rtl"] .multiselect__content {
  text-align: right;
}
*[dir="rtl"] .multiselect__option:after {
  right: auto;
  left: 0;
}
*[dir="rtl"] .multiselect__clear {
  right: auto;
  left: 12px;
}
*[dir="rtl"] .multiselect__spinner {
  right: auto;
  left: 1px;
}
@keyframes spinning {
  from {
    transform: rotate(0);
  }
  to {
    transform: rotate(2turn);
  }
}
</style>
