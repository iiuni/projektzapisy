<script lang="ts">
import axios from "axios";
import Vue from "vue";
import { mapGetters } from "vuex";

import { CourseInfo } from "../../../../enrollment/timetable/assets/store/courses";

interface ProposalInfo extends CourseInfo {
    status: "IN_OFFER" | "IN_VOTE" | "WITHDRAWN";
}

export default Vue.extend({
    data() {
        return {
            courses: [] as ProposalInfo[],
            visibleCourses: [] as ProposalInfo[]
        };
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
        ) as ProposalInfo[];
        this.courses = courseData;
        this.visibleCourses = courseData;

        this.$store.subscribe((mutation, _) => {
            switch (mutation.type) {
                case "filters/registerFilter":
                    this.visibleCourses = this.courses.filter(this.tester);
                    break;
            }
        });
    }
});
</script>

<template>
    <div>
        <ul>
            <li
                v-for="c in visibleCourses"
                v-bind:key="c.id"
                class="mb-1"
                v-bind:class="c.status.toLowerCase()"
            >
                <a :href="c.url">{{ c.name }}</a>
            </li>
        </ul>

        <ul id="proposal-legend" class="text-muted">
            <li class="in_vote">
                Przedmiot poddany pod głosowanie w tym cyklu.
            </li>
            <li class="in_offer">Przedmiot w ofercie ale nie w tym cyklu.</li>
            <li class="withdrawn">
                Przedmiot wycofany z oferty (zarchiwizowany).
            </li>
        </ul>
    </div>
</template>

<style lang="scss" scoped>
// Defines clear colour-codes for the proposal list statuses.
//
// Refers to palette of Bootstrap 4.

.in_vote a {
    color: var(--green);
}

.in_offer a {
    color: var(--blue);
}

.withdrawn a {
    color: var(--gray);
}

#proposal-legend {
    li {
        list-style: none;
        &:before {
            content: "■";
            vertical-align: middle;
            display: inline-block;
            margin-top: -0.3em;
            font-size: 1.5em;
            margin-right: 4px;
            margin-left: -17px;
        }
        &.in_vote:before {
            color: var(--green);
        }

        &.in_offer:before {
            color: var(--blue);
        }

        &.withdrawn:before {
            color: var(--gray);
        }
    }
}
</style>
