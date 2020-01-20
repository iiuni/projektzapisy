<template>
	<div id="user-list">
		<ul class="list-group">
			<li v-for="user in users" v-if="matchChar(user) && match(user)" class="user-list-link mb-1">
				<a v-bind:href="getUrlAddress(user.id)">{{`${user.first_name} ${user.last_name}`}}</a>
			</li>
		</ul>
	</div>
</template>

<script>
	import { EventBus } from './event-bus.js';
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
			let rawUsers = JSON.parse(document.getElementById('user-list-json-container').getAttribute(
					'data') || '{}');
			this.users = Object.values(rawUsers);

			this.users = this.users.sort(function (a, b) {
					if (a.last_name > b.last_name) {
						return 1
					} else if (a.last_name < b.last_name) {
						return -1
					} else {
						return 0
					}
				});
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
			match: function (user) {

				let firstName = user.first_name.toLowerCase();
				let lastName = user.last_name.toLowerCase();
				let emailAddress = user.email;
				let album = "";
				if (user.hasOwnProperty('album')) {
					album = user.album;
				}
				let phrase = this.filter_phrase.toLowerCase().trim();

				return firstName.startsWith(phrase) || lastName.startsWith(phrase) ||
						album.startsWith(phrase) || emailAddress.startsWith(phrase);
			},
			matchChar: function (user) {
				let first_name = user.first_name.toLowerCase();
				let last_name = user.last_name.toLowerCase();
				let button = this.filter_button.toLowerCase();

				if (button != 'wszyscy') {
					return first_name.startsWith(button) || last_name.startsWith(button);
				}
				return true;
			},
			getUrlAddress: function (id) {
				return this.userLinkUrl + id
			},
		}
	}
</script>

<style>
	.user-list-link {
		margin-left: 40px;
		margin-right: 20px;
	}
</style>