<script lang="ts">
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "../../../timetable/assets/store/courses";

export default Vue.extend({
    data() {
        return {
            courses: [] as  CourseInfo[],
            visibleCourses: [] as CourseInfo[],
        }
    },
    computed: {
        ...mapGetters("filters", {
            tester: "visible"
        })
    },
    mounted() {
        // When mounted, load the list of courses from embedded JSON.
        const courseData = JSON.parse(
            document.getElementById("courses-data")!.innerHTML
        ) as CourseInfo[];

        this.$store.subscribe((mutation, _) => {
            switch(mutation.type) {
                case "filters/registerFilter":
                this.visibleCourses = this.courses.filter(this.tester);
                break;
            }
        });
    }
});
</script>

<template>
    <ul>
        <li v-for="c in visibleCourses" v-bind:key="c.id">
            <a :href="c.url">{{ c.name }}</a>
        </li>
    </ul>
</template>