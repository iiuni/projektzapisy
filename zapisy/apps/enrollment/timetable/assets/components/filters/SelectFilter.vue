<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class ExactFilter implements Filter {
    constructor(public option: number|undefined, public propertyName: string) {}

    visible(c: Object): boolean {
        if (this.option === undefined) {
            return true;
        }
        let propGetter = property(this.propertyName) as (
            c: Object
        ) => number;
        let propValue = propGetter(c);
        return propValue == this.option;
    }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
    props: {
        // Property of a course on which we are filtering.
        property: String,
        // Every filter needs a unique identifier.
        filterKey: String,
        options: Array as () => [number, string][],
        placeholder: String
    },
    data: () => {
        return {
            selected: undefined,
        };
    },
    methods: {
        ...mapMutations("filters", ["registerFilter"])
    },
    watch: {
        selected: function(newSelected: number|undefined) {
            this.registerFilter({
                k: this.filterKey,
                f: new ExactFilter(newSelected, this.property)
            });
        }
    },
});
</script>

<template>
    <div class="input-group mb-2">
        <select class="custom-select" v-model="selected">
            <option selected :value="undefined">-- {{ placeholder }} --</option>
            <option v-for="[k, o] of options" :value="k">
                {{ o }}
            </option>
        </select>
    </div>
</template>
