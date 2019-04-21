<script>
import Vue from "vue";
import axios from 'axios';
import Component from "vue-class-component";

export default {
    data () {
        return {
            ns_c: 0,
            nss: [], // structure: [ [id, text, issued on], [...], ... ]
        }
    },
    methods: {
        getCount: function () {
            axios.get('/notifications/count')
            .then((result) => {
                this.ns_c = result.data
            })
        },
        getNotifications: function () {
            axios.get('/notifications/get')
            .then((result) => {
                this.nss = result.data
            })
        },
        deleteAll: function () {
            axios.get('/notifications/delete/all')
            .then((request) => {
                this.nss = request.data
            })
            this.getCount();
        },
        deleteOne: function (id){
            axios.get('/notifications/delete',{
                    params: {
                        issued_on: this.nss[id][2], 
                    }
                }            
            ).then((request) => {
                this.nss = request.data
            })
            this.getCount()
        }
    },
    created () {
        this.getCount()
    }
}

</script>


<template>
<div>
    
    <li class="nav-item dropdown" id="notification-dropdown">
        <a class="nav-link dropdown-toggle specialdropdown" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <i v-if="ns_c == 0" class="far fa-bell bell nav-link" style="padding-right: 0;"></i>
            <i v-else class="fas fa-bell bell nav-link"  style="padding-right: 0;" @click="getNotifications"></i>
        </a>
        <div id="modal-container" class="dropdown-menu dropdown-menu-right m-2">
            <form>
                <p>Lista powiadomień:</p>
                <div v-if="ns_c != 0" class="place-for-notifications">
                    <div v-for="elem in nss" :key="elem[0]" class="onemessage">
                        <div>
                            <div class="textM">
                                {{ elem[1] }}
                            </div>
                            <div class="deleteM" @click="deleteOne(elem[0])">
                                <i class="fas fa-times"></i>
                            </div>
                            <div style="clear: both;"></div>
                        </div>
                    </div>
                </div>
            </form>
            <form>
                <div v-if="ns_c != 0" class="deleteAllM">
                    <a href="#" @click="deleteAll">
                        Usuń wszystkie powiadomienia.
                    </a>
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
    padding-bottom: 12px;
    padding-top: 12px;
    min-width: 350px;
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
  max-height: 500px;
}

#modal-container p {
    display: block;
    width: 100%;
    font-size: 16px;
    color: #00709e;
    font-weight: bold;
    margin-bottom: 8px;
    margin-left: 12px;
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

.place-for-notifications{
    max-height: 395px;
    overflow-y: scroll;
    margin-left: 7px;
    padding-right: 5px;
}

.NoM {
    color: #9c9999;
    text-align: center;
    padding-bottom: 10px;
    padding-top: 10px;
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
    padding-top: 10px;
    border-top: 1px solid #00000021;
}

</style>