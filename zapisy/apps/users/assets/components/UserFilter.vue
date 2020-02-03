<template>
    <div>
        <ul class="list-group list-group-flush border border-default">
            <li class="list-group-item bg-light">
                <fieldset class="small-fieldset">
                    <div class="filter row" id="enr-StudentsList-top-bar">
                        <label for="user-name" class="label label-default p-2">Filtrowanie:&nbsp</label>
                        <div id="user-name" class="mt-1 mb-1">
                            <input class="form-control" type="text" v-bind:value="input_value" v-on:input="emitInputFilter"/>
                        </div>
                    </div>
                </fieldset>
            </li>
            <li class="list-group-item bg-light">
                <div id="user-alpha-list">
                    <ul id="user-list-menu">
                        <li v-for="char in chars" class="charFilter">
                            <button class="btn btn-link p-1" v-on:click="emitCharFilter(char)" >{{char}}</button>
                        </li>
                    </ul>
                </div>
            </li>
        </ul>
    </div>
</template>


<script lang="ts">
import { EventBus } from './event-bus';

export default {
    data: function() {
        return {
            input_value: "",
            chars: ['A', 'B', 'C', 'Ć', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Ł', 'M', 'N', 'Ń', 'O', 'Q',
                'P', 'R', 'S', 'Ś', 'T', 'U', 'W', 'X', 'Y', 'Z', 'Ż', 'Ź', 'Wszyscy']
        }
    },
    name: "StudentFilter",
    methods: {
        emitInputFilter: function(event) {
            this.input_value = event.target.value;
            EventBus.$emit('user-input-filter', event.target.value);
        },
        emitCharFilter: function(char) {
            EventBus.$emit('user-char-filter', char);
        }
    }
};
</script>

<style>
    .charFilter {
        display: inline;
    }
</style>