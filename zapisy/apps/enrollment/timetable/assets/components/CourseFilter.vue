<script lang="ts">
import { cloneDeep, sortBy, toPairs } from "lodash";
import Vue from "vue";

import TextFilter from "./filters/TextFilter.vue";
import LabelsFilter from "./filters/LabelsFilter.vue";
import SelectFilter from "./filters/SelectFilter.vue";
import CheckFilter from "./filters/CheckFilter.vue";
import { FilterDataJSON, KVDict } from "./../models";

export default Vue.extend({
    components: {
        TextFilter,
        LabelsFilter,
        SelectFilter,
        CheckFilter
    },
    data: function() {
        return {
            allEffects: {},
            allTags: {},
            allOwners: [] as [number, string][],
            allTypes: {},

            // The filters are going to be collapsed by default.
            collapsed: true
        };
    },
    created: function() {
        const filtersData = JSON.parse(
            document.getElementById("filters-data")!.innerHTML
        ) as FilterDataJSON;
        this.allEffects = cloneDeep(filtersData.allEffects);
        this.allTags = cloneDeep(filtersData.allTags);
        this.allOwners = sortBy(
            toPairs(filtersData.allOwners),
            ([k, [a, b]]) => {
                return b;
            }
        ).map(([k, [a, b]]) => {
            return [Number(k), `${a} ${b}`] as [number, string];
        });
        this.allTypes = toPairs(filtersData.allTypes);
    }
});
</script>

<template>
    <div class="card bg-light">
        <div class="card-body" v-bind:class="{ collapsed: collapsed }">
            <div class="row">
                <div class="col-md">
                    <TextFilter
                        filterKey="name-filter"
                        property="name"
                        placeholder="Nazwa przedmiotu"
                    />
                    <hr />
                    <LabelsFilter
                        title="Tagi"
                        filterKey="tags-filter"
                        property="tags"
                        :allLabels="allTags"
                        onClass="badge-success"
                    />
                </div>
                <div class="col-md">
                    <SelectFilter
                        filterKey="type-filter"
                        property="courseType"
                        :options="allTypes"
                        placeholder="Rodzaj przedmiotu"
                    />
                    <hr />
                    <LabelsFilter
                        title="Efekty kształcenia"
                        filterKey="effects-filter"
                        property="effects"
                        :allLabels="allEffects"
                        onClass="badge-info"
                    />
                </div>
                <div class="col-md">
                    <SelectFilter
                        filterKey="owner-filter"
                        property="owner"
                        :options="allOwners"
                        placeholder="Opiekun przedmiotu"
                    />
                    <hr />
                    <CheckFilter
                        filterKey="freshmen-filter"
                        property="recommendedForFirstYear"
                        label="Pokaż tylko przedmioty zalecane dla pierwszego roku"
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
        background: linear-gradient(to top,
            rgba(248,249,250, 1) 0%, 
            rgba(248,249,250, 0) 100%
        );
        pointer-events: none; /* so the text is still selectable */
    }
}

// Follows the Bootstrap 4 media query breakpoint.
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
