<template>
    <div class="alert alert-info" 
            :class="{'alert-danger': exceedsLimit }">
        Wykorzystano {{ total }} z {{ limit }} punktów
    </div>
</template>


<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import { sum, values } from "lodash";

// The component displaying the message will get two inputs. One is a point
// limit, the other is a map of point values from input fields, keyed by the
// input id.
const counterComponentProps = Vue.extend({
    props: {
        inputs: Object as () => { [key: string]: number },
        limit: Number,
    },
});
@Component
export default class CounterComponent extends counterComponentProps {
    // Computes the total number of points in inputs.
    get total(): number {
        return sum(values(this.inputs));
    }

    get exceedsLimit(): boolean {
        return this.total > this.limit;
    }
}
</script>
