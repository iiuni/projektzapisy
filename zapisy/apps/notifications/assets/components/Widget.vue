<script>
import Vue from "vue";
import Component from "vue-class-component";

export default {
    data () {
        return {
            ns: JSON.parse(document.getElementById("notifications-data").innerHTML),
            ns_c: JSON.parse(document.getElementById("notification_counter-data").innerHTML),
            show: false,
        }
    },
    methods: {
        change: function(){
            if(this.show){
                this.show = false
            }else{
                this.show = true
            }
            console.log(this.show)
        }
    },
}
</script>

<template>
<div>
    <div v-on:click="change">
        <i v-if="ns_c == '0'" class="far fa-bell bell nav-link"></i>
        <i v-else class="fas fa-bell bell nav-link bellalert"></i>
    </div>

    <div v-show="show">HAAAALO</div>
</div>
</template>

<style>
.bell{
    font-size: 20px;
    padding-top: 8px;
    padding-bottom: 8px;
}
.bellalert
{
    color: rgb(235, 235, 80);
}
</style>