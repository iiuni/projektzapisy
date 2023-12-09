<script lang="ts">
import { cloneDeep, toPairs } from "lodash";
import Vue from "vue";

import { mapMutations } from "vuex";

import TextFilter from "./filters/TextFilter.vue";
import LabelsFilter from "./filters/LabelsFilter.vue";
import MultiSelectFilter from "./filters/MultiSelectFilter.vue";
import CheckFilter from "./filters/CheckFilter.vue";
import { FilterDataJSON, MultiselectFilterData } from "./../models";

export default Vue.extend({
  components: {
    TextFilter,
    LabelsFilter,
    CheckFilter,
    MultiSelectFilter,
  },
  data: function () {
    return {
      allEffects: {},
      allTags: {},
      allOwners: [] as MultiselectFilterData<number>,
      allTypes: [] as MultiselectFilterData<number>,
      // The filters are going to be collapsed by default.
      collapsed: true,
    };
  },
  created: function () {
    const filtersData = JSON.parse(
      document.getElementById("filters-data")!.innerHTML
    ) as FilterDataJSON;
    this.allEffects = cloneDeep(filtersData.allEffects);
    this.allTags = cloneDeep(filtersData.allTags);
    this.allOwners = toPairs(filtersData.allOwners)
      .sort(([id, [firstname, lastname]], [id2, [firstname2, lastname2]]) => {
        const lastNamesComparison = lastname.localeCompare(lastname2, "pl");
        return lastNamesComparison === 0
          ? firstname.localeCompare(firstname2, "pl")
          : lastNamesComparison;
      })
      .map(([id, [firstname, lastname]]) => {
        return { value: Number(id), label: `${firstname} ${lastname}` };
      });
    this.allTypes = Object.keys(filtersData.allTypes).map(
      (typeKey: string) => ({
        value: Number(typeKey),
        label: filtersData.allTypes[Number(typeKey)],
      })
    );
  },
  mounted: function () {
    // Extract filterable properties names from the template.
    const filterableProperties = Object.values(this.$refs)
      .filter((ref: any) => ref.filterKey)
      .map((filter: any) => filter.property);
    // Expand the filters if there are any initially specified in the search params.
    const searchParams = new URL(window.location.href).searchParams;
    if (filterableProperties.some((p: string) => searchParams.has(p))) {
      this.collapsed = false;
    }
  },
  methods: {
    ...mapMutations("filters", ["clearFilters"]),
  },
});
</script>

<template>
  <div class="card bg-light filters-card">
    <div class="card-body" v-bind:class="{ collapsed: collapsed }">
      <div class="row position-relative">
        <div class="col-md">
          <TextFilter
            filterKey="name-filter"
            property="name"
            placeholder="Nazwa przedmiotu"
            ref="name-filter"
          />
          <hr />
          <LabelsFilter
            title="Tagi"
            filterKey="tags-filter"
            property="tags"
            :allLabels="allTags"
            onClass="bg-success"
            ref="tags-filter"
          />
        </div>
        <div class="col-md">
          <MultiSelectFilter
            filterKey="type-filter"
            property="courseType"
            :options="allTypes"
            title="Rodzaj przedmiotu"
            placeholder="Wszystkie rodzaje"
            ref="type-filter"
          />
          <hr />
          <LabelsFilter
            title="Efekty kształcenia"
            filterKey="effects-filter"
            property="effects"
            :allLabels="allEffects"
            onClass="bg-info"
            ref="effects-filter"
          />
        </div>
        <div class="col-md">
          <MultiSelectFilter
            filterKey="owner-filter"
            property="owner"
            :options="allOwners"
            title="Opiekun przedmiotu"
            placeholder="Wszyscy opiekunowie"
            ref="owner-filter"
          />
          <hr />
          <CheckFilter
            filterKey="freshmen-filter"
            property="recommendedForFirstYear"
            label="Pokaż tylko przedmioty zalecane dla pierwszego roku"
            ref="freshmen-filter"
          />
          <hr />
          <button
            class="btn btn-outline-secondary"
            type="button"
            @click="clearFilters()"
          >
            Wyczyść filtry
          </button>
        </div>
      </div>
    </div>
    <div class="card-footer p-1 text-center">
      <a href="#" @click.prevent="collapsed = !collapsed">zwiń / rozwiń</a>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.collapsed {
  overflow-y: hidden;
  height: 120px;

  // Blurs over the bottom of filter card.
  &:after {
    position: absolute;
    display: block;
    // Height of the card footer.
    bottom: 28px;
    left: 0;
    height: 50%;
    width: 100%;
    content: "";
    // Bootstrap light colour.
    background: linear-gradient(
      to top,
      rgba(248, 249, 250, 1) 0%,
      rgba(248, 249, 250, 0) 100%
    );
    pointer-events: none; /* so the text is still selectable */
  }
}

// Follows the Bootstrap 5 media query breakpoint.
@media (max-width: 767px) {
  .col-md + .col-md {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding-top: 1em;
  }
}

.card-footer {
  height: 28px;
}

.filters-card {
  transform: scale(1);
  z-index: 2;
}
</style>
