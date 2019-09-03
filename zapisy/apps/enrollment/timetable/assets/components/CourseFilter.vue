<script lang="ts">
import { cloneDeep } from "lodash";
import Vue from "vue";

import TextFilter from "./filters/TextFilter.vue";
import LabelsFilter from "./filters/LabelsFilter.vue";
import { FilterDataJSON, KVDict } from "./../models";

export default Vue.extend({
    components: {
        TextFilter,
        LabelsFilter,
    },
    data: function() {
        return {
            allEffects: undefined,
            allTags: undefined,
            allOwners: undefined,
        }
    },
    created: function() {
        const filtersData = JSON.parse(
            document.getElementById("filters-data")!.innerHTML
        ) as FilterDataJSON;
        this.allEffects = cloneDeep(filtersData.allEffects);
        this.allTags = cloneDeep(filtersData.allTags);
        this.allOwners = cloneDeep(filtersData.allOwners);
    },
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
                    <hr>
                    <LabelsFilter
                        title="Tagi"
                        filterKey="tags-filter"
                        property="tags"
                        :allLabels="allTags"
                    />
                </div>
                <div class="col-md-4">
                    <LabelsFilter
                        title="Efekty kształcenia"
                        filterKey="effects-filter"
                        property="effects"
                        :allLabels="allEffects"
                    />
                </div>
                <div class="col-md-4"></div>
            </div>
        </div>
    </div>
</template>
