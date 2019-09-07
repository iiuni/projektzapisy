<script lang="ts">
import axios from "axios";
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "@/enrollment/timetable/assets/store/courses";

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
        this.courses = courseData;
        this.visibleCourses = courseData;

        this.$store.subscribe((mutation, _) => {
            switch(mutation.type) {
                case "filters/registerFilter":
                this.visibleCourses = this.courses.filter(this.tester);
                break;
            }
        });
    },
});
</script>

<template>
    <ul>
        <li v-for="c in visibleCourses" v-bind:key="c.id" class="mb-1">
            <a :href="c.url">{{ c.name }}</a>
        </li>
    </ul>
</template>