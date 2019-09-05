<script lang="ts">
import { property } from "lodash";
import Vue from "vue";
import { mapMutations } from "vuex";

import { CourseInfo } from "../../store/courses";
import { Filter } from "../../store/filters";

class TextFilter implements Filter {
    constructor(
        public pattern: string = "",
        public propertyName: string
    ) {}

    visible(c: CourseInfo): boolean {
        let propGetter = property(this.propertyName) as (
            c: CourseInfo
        ) => string;
        let propValue = propGetter(c);
        return propValue
            .toLocaleLowerCase()
            .includes(this.pattern.toLocaleLowerCase());
    }
}

// TextFilter applies the string filtering on a property of a course.
export default Vue.extend({
    props: {
        // Property of a course on which we are filtering.
        property: String,
        // Every filter needs a unique identifier.
        filterKey: String,
        placeholder: String,
    },
    data: () => {
        return {
            pattern: "",
        }
    },
    methods: {
        ...mapMutations("filters", ["registerFilter"])
    },
    watch: {
        pattern: function(newPattern: string, _) {
            this.registerFilter(
                {k: this.filterKey,
                f: new TextFilter(newPattern, this.property)}
            );
        }
    }
});
</script>

<template>
    <div class="input-group mb-2">
        <input class="form-control" type="text" 
            v-model="pattern" :placeholder="placeholder">
        <div class="input-group-append">
            <button class="btn btn-outline-secondary" type="button" 
                @click="pattern = ''">&times;</button>
        </div>
    </div>
</template>
