<script>
import Vue from "vue";
import Component from "vue-class-component";

export default {
    data () {
        return {
            ns: JSON.parse(document.getElementById("notifications-data").innerHTML),
            ns_c: JSON.parse(document.getElementById("notification_counter-data").innerHTML),
            showModal: false,
        }
    },
    methods: {
        change: function(){
            this.showModal = !this.showModal
            console.log(this.showModal)
        },
        close: function(){
            this.showModal = false
        }
    },
}

</script>


<template>
<div>
    <div @click="change">
        <i v-if="ns_c == 0" class="far fa-bell bell nav-link"></i>
        <i v-else class="fas fa-bell bell nav-link"></i>
    </div>

    <div class="triangle" v-show="showModal"></div>
    <div id="modal-container" v-show="showModal">
        <p>Lista powiadomień:</p>
        <div v-if="ns_c != 0">
            <div v-for="elem in ns" :key="elem" class="onemessage">
                <div class="textM">
                    {{ elem }}
                </div>
                <div class="deleteM">
                    <i class="fas fa-times"></i>
                </div>
            </div>
            <div class="deleteAllM">
                Usuń wszystkie powiadomienia.
            </div>
        </div>
        <div v-else class="NoM">
            Brak nowych powiadomień.
        </div>
    </div>

</div>
</template>

<style>
.bell{
    font-size: 20px;
    padding-top: 8px;
    padding-bottom: 8px;
}
#modal-container {
  display: block;
  position: absolute;
  width: 400px;
  z-index: 9998;
  min-height: 50px;
  top: 45px;
  right: 300px;
  padding: 17px 3px 10px;
  background-color: #fff;
  border-radius: 2px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, .33);
  transition: all .3s ease;
  font-family: Helvetica, Arial, sans-serif;
  overflow-y: scroll;
}

.triangle {
  width: 0;
    height: 0;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-bottom: 5px solid rgb(255, 255, 255);
    position: absolute;
    top: 40px;
    right: 334px;
}

#modal-container p {
    display: block;
    width: 100%;
    padding-left: 10px;
    font-size: 16px;
    color: #00709e;
    font-weight: bold;
}

.onemessage {
    display: block;
    background-color: #00709e03;
    margin-left: 5px;
    margin-right: 5px;
    min-height: 50px;
    padding: 5px;
    padding-top: 0;
    border: 1px solid #9a9da02e;
    border-radius: 3px;
    margin-top: 5px;
    margin-bottom: 5px;
}

.onemessage:hover{
    background-color: #00709e12;
}

.NoM {
    color: #9c9999;
    text-align: center;
}

.deleteM {
    font-size: 15px;
    float: right;
    color: #615353;
}

.textM {
    float: left;
    padding-top: 5px;
}

.deleteAllM {
    width: 100%;
    text-align: center;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #00000021;
}

</style>