<script lang="ts">
import { cloneDeep, toPairs } from "lodash";
import Vue from "vue";

import { mapGetters } from "vuex";

import TextFilter from "@/enrollment/timetable/assets/components/filters/TextFilter.vue";
import LabelsFilter from "@/enrollment/timetable/assets/components/filters/LabelsFilter.vue";
import MultiSelectFilter from "@/enrollment/timetable/assets/components/filters/MultiSelectFilter.vue";
import SelectFilter from "@/enrollment/timetable/assets/components/filters/SelectFilter.vue";
import CheckFilter from "@/enrollment/timetable/assets/components/filters/CheckFilter.vue";
import { FilterDataJSON } from "@/enrollment/timetable/assets/models";

export default Vue.extend({
  components: {
    TextFilter,
    LabelsFilter,
    SelectFilter,
    CheckFilter,
    MultiSelectFilter,
  },
  props: { refreshFun: Function },
  data: function () {
    return {
      allEffects: {},
      allTags: {},
      allOwners: [] as Array<{ value: number; label: string }>,
      allSemesters: [] as Array<{ value: string; label: string }>,
      allStatuses: [] as Array<{ value: string; label: string }>,
      allTypes: {},

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
      .sort(([k1, [a1, b1]], [k2, [a2, b2]]) => {
        return b1.localeCompare(b2, "pl");
      })
      .map(([k, [a, b]]) => {
        return { value: Number(k), label: `${a} ${b}` };
      });

    this.allTypes = Object.keys(filtersData.allTypes).map(
      (typeKey: string) => ({
        value: Number(typeKey),
        label: filtersData.allTypes[Number(typeKey)],
      })
    );
    this.allSemesters = [
      { value: "z", label: "zimowy" },
      { value: "l", label: "letni" },
      { value: "u", label: "nieokreślony" },
    ];
    this.allStatuses = [
      { value: "IN_OFFER", label: "w ofercie" },
      { value: "IN_VOTE", label: "poddany pod głosowanie" },
      { value: "WITHDRAWN", label: "wycofany z oferty" },
    ];
  },
  computed: {
    ...mapGetters("filters", {
      tester: "visible",
    }),
  },
  mounted() {
    // Extract filterable properties names from the template.
    const filterableProperties = Object.values(this.$refs)
      .filter((ref: any) => ref.filterKey)
      .map((filter: any) => filter.property);
    // Expand the filters if there are any initially specified in the search params.
    const searchParams = new URL(window.location.href).searchParams;
    if (filterableProperties.some((p: string) => searchParams.has(p))) {
      this.collapsed = false;
    }

    this.$store.subscribe((mutation, _) => {
      switch (mutation.type) {
        case "filters/registerFilter":
          this.refreshFun(this.tester);
          break;
      }
    });
  },
});
</script>

<template>
  <div class="card bg-light">
    <div class="card-body" v-bind:class="{ collapsed: collapsed }">
      <div class="row">
        <div class="col-md">
          <TextFilter
            filterKey="name-filter"
            ref="name-filter"
            property="name"
            placeholder="Nazwa przedmiotu"
          />
          <hr />
          <LabelsFilter
            title="Tagi"
            filterKey="tags-filter"
            ref="tags-filter"
            property="tags"
            :allLabels="allTags"
            onClass="bg-success"
            ref="tags-filter"
          />
        </div>
        <div class="col-md">
          <MultiSelectFilter
            filterKey="type-filter"
            ref="type-filter"
            property="courseType"
            :options="allTypes"
            placeholder="Rodzaj przedmiotu"
          />
          <hr />
          <LabelsFilter
            title="Efekty kształcenia"
            filterKey="effects-filter"
            ref="effects-filter"
            property="effects"
            :allLabels="allEffects"
            onClass="bg-info"
            ref="effects-filter"
          />
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
</style>
