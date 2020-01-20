<template>
    <div>
        <ul class="list-group list-group-flush">
            <li class="list-group-item bg-light">
                <fieldset class="small-fieldset">
                    <div class="filter row" id="enr-StudentsList-top-bar">
                        <label for="student_name" class="label label-default">Filtrowanie:&nbsp</label>
                        <div class="main-filter-input">
                            <input class="form-control" id="student_name" type="text" v-bind:value="input_value" v-on:input="emitInputFilter"/>
                        </div>
                    </div>
                </fieldset>
            </li>
            <li class="list-group-item bg-light">
            <div id="user-alpha-list">
                <ul id="user-list-menu">
                    <li v-for="char in chars" class="charFilter">
        				<button class="btn btn-link" v-on:click="emitCharFilter(char)" >{{char}}</button>
                    </li>
                </ul>
            </div>
        </li>
        </ul>
    </div>
</template>


<script lang="ts">
import Vue from "vue";
import { EventBus } from './event-bus';

    export default Vue.extend({
        data: function() {
            return {
                input_value: "",
                chars: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'Ł', 'M', 'N', 'O',
                'P', 'R', 'S', 'T', 'U', 'W', 'Y', 'Z', 'Wszyscy']
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
    });

</script>

<style>
    .charFilter {
        display: inline;
    }
    .btn {
        padding-top: 0.40rem;
        padding-right: 0.20rem;
        padding-bottom: 0.20rem;
        padding-left: 0.40rem;
    }
    .label {
        padding-top: 0.40rem;
        padding-right: 0.20rem;
        padding-bottom: 0.20rem;
        padding-left: 0.40rem;
    }
    #user-list-menu {
        padding-left: 0.40rem;
    }
</style>