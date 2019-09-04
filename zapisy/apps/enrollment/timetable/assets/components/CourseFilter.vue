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
        CheckFilter,
    },
    data: function() {
        return {
            allEffects: {},
            allTags: {},
            allOwners: [] as [number, string][],
            allTypes: {}
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
    <div class="card">
        <div class="card-body">
            <div class="row">
                <div class="col-md-4">
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
                    />
                </div>
                <div class="col-md-4">
                    <SelectFilter
                        filterKey="type-filter"
                        property="courseType"
                        :options="allTypes"
                        placeholder="Rodzaj przedmiotu"
                    />
                    <hr>
                    <LabelsFilter
                        title="Efekty kształcenia"
                        filterKey="effects-filter"
                        property="effects"
                        :allLabels="allEffects"
                    />
                </div>
                <div class="col-md-4">
                    <SelectFilter
                        filterKey="owner-filter"
                        property="owner"
                        :options="allOwners"
                        placeholder="Opiekun przedmiotu"
                    />
                    <hr>
                    <CheckFilter
                        filterKey="freshmen-filter"
                        property="recommendedForFirstYear"
                        label="Pokaż tylko przedmioty zalecane dla pierwszego roku"
                    />
                </div>
            </div>
        </div>
    </div>
</template>
