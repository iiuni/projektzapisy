<script lang="ts">
import Vue from "vue";

import TextFilter from "./filters/TextFilter.vue";

export default Vue.extend({
    components: {
        TextFilter,
    },
});
</script>

<template>
    <div class="card">
        <div class="card-body">
            <TextFilter
                filterKey="name-filter"
                property="name"
                placeholder="Nazwa przedmiotu"/>
        </div>
    </div>
</template>
