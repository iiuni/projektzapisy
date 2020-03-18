<template>
    <div class="card bg-light">
        <div class="card-body">
            <input class="form-control" type="text" :value="input_value" @input="emitInputFilter"
                placeholder="Filtrowanie"/>
            <hr>
            <button v-for="char in chars" :key="char" class="btn btn-link p-1" v-on:click="emitCharFilter(char)"
                    :class="{'text-dark': selectedChar === char}">{{char}}
            </button>
        </div>
    </div>
</template>


<script lang="js">
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
    }
};
</script>
