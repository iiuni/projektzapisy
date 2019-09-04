<script lang="ts">
import {
    property,
    intersection,
    isEmpty,
    keys,
    fromPairs,
    filter
} from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";
import { KVDict } from "../../models";

class IntersectionFilter implements Filter {
    constructor(public ids: number[] = [], public propertyName: string) {}

    visible(c: Object): boolean {
        if (isEmpty(this.ids)) {
            return true;
        }
        const propGetter = property(this.propertyName) as (c: Object) => number[];
        const propValue = propGetter(c);
        const common = intersection(this.ids, propValue);
        return !isEmpty(common);
    }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
    props: {
        // Property of a course on which we are filtering.
        property: String,
        // Every filter needs a unique identifier.
        filterKey: String,
        allLabels: Object as () => KVDict,
        title: String,
        // CSS class to apply to the badge when it's on.
        onClass: String,
    },
    computed: {
        allLabelKeys: function() {
            return keys(this.allLabels);
        }
    },
    data: () => {
        return {
            selected: {} as { [k: number]: boolean }
        };
    },
    methods: {
        ...mapMutations("filters", ["registerFilter"]),
        toggle(key: number) {
            this.selected[key] = !this.selected[key];

            const selectedIds = keys(this.selected)
                .map(Number)
                .filter((k: number) => {
                    return this.selected[k];
                });
            this.registerFilter({
                k: this.filterKey,
                f: new IntersectionFilter(selectedIds, this.property)
            });
        }
    },
    // When the component is mounted we set all the labels as selected.
    mounted: function() {
        this.selected = fromPairs(keys(this.allLabels).map(k => [k, false]));
    }
});
</script>

<template>
    <div class="mb-3 overflow-hidden">
        <h4>{{ title }}</h4>
        <a href="#"
            v-for="l in allLabelKeys"
            class="badge"
            v-bind:class="[selected[l] ? onClass : 'badge-secondary']"
            @click.prevent="toggle(l)"
        >
            {{ allLabels[l] }}
        </a>
    </div>
</template>
