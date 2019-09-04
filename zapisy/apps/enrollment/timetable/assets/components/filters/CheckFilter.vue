<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { Filter } from "../../store/filters";

class BooleanFilter implements Filter {
    constructor(public on: boolean, public propertyName: string) {}

    visible(c: Object): boolean {
        if (!this.on) {
            return true;
        }
        let propGetter = property(this.propertyName) as (
            c: Object
        ) => boolean;
        let propValue = propGetter(c);
        return propValue;
    }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
    props: {
        // Property of a course on which we are filtering.
        property: String,
        // Every filter needs a unique identifier.
        filterKey: String,
        label: String
    },
    data: () => {
        return {
            on: false,
        };
    },
    methods: {
        ...mapMutations("filters", ["registerFilter"])
    },
    watch: {
        on: function(newOn: boolean) {
            this.registerFilter({
                k: this.filterKey,
                f: new BooleanFilter(newOn, this.property)
            });
        }
    },
});
</script>

<template>
    <div class="input-group">
       <div class="custom-control custom-checkbox">
            <input type="checkbox" class="custom-control-input" :id="filterKey" v-model="on">
            <label class="custom-control-label" :for="filterKey">{{ label }}</label>
        </div>
    </div>
</template>
