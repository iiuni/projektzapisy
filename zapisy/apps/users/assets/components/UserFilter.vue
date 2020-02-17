<template>
    <div class="card bg-light">
        <div class="row card-body mx-1 mt-1 mb-0 p-2 border-bottom">
            <div class="col-md-4">
                <label for="user-name" class="label label-default">Filtrowanie:&nbsp</label>
                <div id="user-name" class="mt-1 mb-1">
                    <input class="form-control" type="text" v-bind:value="input_value" v-on:input="emitInputFilter"/>
                </div>
            </div>
        </div>
        <div class="row card-body m-1 p-1">
            <div class="col-md-12">
                <span v-for="char in chars" class="charFilter">
                    <button class="btn btn-link p-1" v-on:click="emitCharFilter(char)"
                            :class="{active: selectedButton(char)}">{{char}}
                    </button>
                </span>
            </div>
        </div>
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