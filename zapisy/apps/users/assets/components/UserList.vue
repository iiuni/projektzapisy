<template>
	<div id="students-list">
		<h3>Lista studentów</h3>
		<ul class="students">
			<li v-for="student in students" v-if="matchChar(student) && match(student)" class="mb-1">
				<a v-bind:href="getUrlAddress(student.id)">{{student.first_name + " " + student.last_name}}</a>
			</li>
		</ul>
	</div>

</template>

<script>
	import { EventBus } from './event-bus.js';
    export default {
		name: "StudentList",
		data: function () {
			return {
				filter_phrase: '',
				filter_button: '',
				students: [],
			}
		},
		beforeMount: function() {
			this.students = JSON.parse(document.getElementById('student-json-container').getAttribute('data') || '{}');
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
			match: function(student) {
				let first_name = student.first_name.toLowerCase();
				let last_name = student.last_name.toLowerCase();
				let phrase = this.filter_phrase.toLowerCase();

				return first_name.startsWith(phrase) || last_name.startsWith(phrase);
			},
			matchChar: function(student) {
				let first_name = student.first_name.toLowerCase();
				let last_name = student.last_name.toLowerCase();
				let button = this.filter_button.toLowerCase();

				if (button != 'wszyscy')
				{
					return first_name.startsWith(button) || last_name.startsWith(button);
				}
				return true;
			},
			getUrlAddress: function(id) {
				return '/users/profile/student/' + id
			}
		}
	}
</script>
