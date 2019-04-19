<script>
import Vue from "vue";
import axios from 'axios';
import Component from "vue-class-component";

export default {
    data () {
        return {
            ns: JSON.parse(document.getElementById("notifications-data").innerHTML),
            ns_c: JSON.parse(document.getElementById("notification_counter-data").innerHTML),
            nss: [],
        }
    },
    methods: {
        getNotifications: function () {
            axios.get('/notifications/get')
            .then((result) => {
                console.log(result.data)
                this.nss = result.data
            })
        }
    },
}

</script>


<template>
<div>
    
    <li class="nav-item dropdown" id="notification-dropdown">
        <a class="nav-link dropdown-toggle specialdropdown" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" @click="getNotifications">
            <i v-if="ns_c == 0" class="far fa-bell bell nav-link" style="padding-right: 0;"></i>
            <i v-else class="fas fa-bell bell nav-link"  style="padding-right: 0;"></i>
        </a>
        <div id="modal-container" class="dropdown-menu dropdown-menu-right m-2">
            <form>
                <p>Lista powiadomień:</p>
                <div v-if="ns_c != 0">
                    <div>
                        <div v-for="elem in nss" :key="elem" class="onemessage">
                            <div>
                                <div class="textM">
                                    {{ elem }}
                                </div>
                                <div class="deleteM">
                                    <i class="fas fa-times"></i>
                                </div>
                                <div style="clear: both;"></div>
                            </div>
                        </div>
                    </div>
                    <div class="deleteAllM">
                        <a href="">Usuń wszystkie powiadomienia.</a>
                    </div>
                </div>
                <div v-else class="NoM">
                    Brak nowych powiadomień.
                </div>
            </form>
        </div>
    </li>

</div>
</template>

<style>
#notification-dropdown .dropdown-menu{
    background: rgb(248, 249, 250);
    padding: 12px;
    width: 350px;
    padding-bottom: 0;
}
.specialdropdown::after{
    content: none;
}
.dropdown-menu-right{
    right: -160px;
}
.bell{
    font-size: 23px;
    padding: 0;
}
#modal-container {
  overflow-y: scroll;
  max-height: 500px;
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
    padding-bottom: 5px;
    width: 260px;
}

.deleteAllM {
    width: 100%;
    text-align: center;
    margin-top: 15px;
    padding-top: 10px;
    border-top: 1px solid #00000021;
    padding-bottom: 12px;
}

</style>