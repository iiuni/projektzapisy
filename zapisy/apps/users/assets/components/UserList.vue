<template>
    <div id="user-list">
        <ul>
            <div v-for="user in users" :key="user.id" class="mb-1">
                <li v-if="matchChar(user) && matchInput(user)">
                    <a :href="getUrlAddress(user.id)">{{user.first_name}} {{user.last_name}}</a>
                </li>
            </div>
        </ul>
    </div>
</template>
<script lang="js">
import { EventBus } from './event-bus';
import { sortBy, some, every, map, get } from 'lodash';

export default {
    name: "UserList",
    data: function () {
        return {
            filter_phrase: '',
            filter_button: '',
            users: [],
            userLinkUrl: '',
        }
    },
    beforeMount: function () {
        let rawUsers = JSON.parse(document.getElementById('user-list-json-script').textContent);
        this.users = Object.values(rawUsers);
        this.users = sortBy(this.users, ["last_name", "first_name"]);
        this.userLinkUrl = document.getElementById('user-link').getAttribute('data');
    },
    mounted: function () {
        EventBus.$on('user-char-filter', value => {
            this.filter_button = value
        });
        EventBus.$on('user-input-filter', value => {
            this.filter_phrase = value
        });
    },
    methods: {
        matchInput: function (user) {
            // Remove trailing/leading whitespaces from input
            let phrase = this.filter_phrase.toLowerCase().trim();
            const regex = /\s+/;
            let words = phrase.split(regex);

            const props = [
                        "first_name",
                        "last_name",
                        "email",
                        "album",
                    ];
            const values = map(props, (p) => get(user, p, "").toLowerCase());
            const anyPropMatches = (word) => !some(values, (v) => v.startsWith(word));
            return !every(words, anyPropMatches);
        },
        matchChar: function (user) {
            let last_name = user.last_name.toLowerCase();
            let button = this.filter_button.toLowerCase();

            if (button != 'wszyscy') {
                return last_name.startsWith(button);
            }
            return true;
        },
        getUrlAddress: function (id) {
            return this.userLinkUrl + id
        },
    }
}
</script>
