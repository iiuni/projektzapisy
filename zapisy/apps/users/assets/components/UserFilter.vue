<template>
    <div>
        <ul class="list-group list-group-flush border border-default">
            <li class="list-group-item bg-light">
                <fieldset class="small-fieldset">
                    <div class="filter row ml-1" id="enr-StudentsList-top-bar">
                        <label for="user-name" class="label label-default p-2">Filtrowanie:&nbsp</label>
                        <div id="user-name" class="mt-1 mb-1">
                            <input class="form-control" type="text" v-bind:value="input_value" v-on:input="emitInputFilter"/>
                        </div>
                    </div>
                </fieldset>
            </li>
            <li class="list-group-item bg-light">
                <ul id="user-list-menu">
                    <li v-for="char in chars" class="charFilter">
                        <button class="btn btn-link p-1" v-on:click="emitCharFilter(char)"
                                :class="{active: selectedButton(char)}">{{char}}
                        </button>
                    </li>
                </ul>
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
                'P', 'R', 'S', 'Ś', 'T', 'U', 'W', 'X', 'Y', 'Z', 'Ż', 'Ź', 'Wszyscy'],
            selectedChar: "Wszyscy",
        }
    },
    name: "StudentFilter",
    methods: {
        emitInputFilter: function(event) {
            this.input_value = event.target.value;
            EventBus.$emit('user-input-filter', event.target.value);
        },
        emitCharFilter: function(char) {
            this.selectedChar = char;
            EventBus.$emit('user-char-filter', char);
        },
        selectedButton: function(char) {
            return char == this.selectedChar;
        }
    }
};
</script>

<style>
    .charFilter {
        display: inline;
    }
    .btn-link:focus {
        text-decoration: none;
    }
    .btn-link:hover {
        text-decoration: none;
        color: black;
    }
    .active {
        color: black;
        text-decoration: none;
    }
</style>