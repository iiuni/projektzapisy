<script>
import Vue from "vue";
import Component from "vue-class-component";

export default {
    data () {
        return {
            ns: JSON.parse(document.getElementById("notifications-data").innerHTML),
            ns_c: JSON.parse(document.getElementById("notifications_counter-data").innerHTML),
        }
    },
}
</script>

<template>
<div>
    <i v-if="ns_c == 0" class="far fa-bell bell nav-link"></i>
    <i v-else class="fas fa-bell bell nav-link"></i>
    
    <div v-if="show">
        halo
    </div>
</template>

<style>
.bell{
    font-size: 20px;
    padding-top: 8px;
    padding-bottom: 8px;
}
</style>