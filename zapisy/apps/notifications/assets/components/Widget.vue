<script>
import Vue from "vue";
import axios from 'axios';
import Component from "vue-class-component";

export default {

    data () {
        return {
            n_counter: 0,
            n_array: [], // structure: [ [id, text, issued on], [...], ... ]
        }
    },
    methods: {
        getCount: function () {
            axios.get('/notifications/count')
            .then((result) => {
                this.n_counter = result.data
            })
        },
        getNotifications: function () {
            axios.get('/notifications/get')
            .then((result) => {
                this.n_array = result.data
            })
        },
        deleteAll: function () {
            axios.defaults.xsrfCookieName = 'csrftoken';
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';

            axios.post('/notifications/delete/all')
            .then((request) => {
                this.n_array = request.data
            })
            this.getCount();
        },
        deleteOne: function (i){
            axios.defaults.xsrfCookieName = 'csrftoken';
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';

            var FormBody = new FormData();
            FormBody.append('issued_on', this.n_array[i].issued_on);
            FormBody.append('id', this.n_array[i].id);

            axios({
                method: 'post',
                url: '/notifications/delete',
                data: FormBody,
                config: {
                    headers: {
                        'Content-Type': 'multipart/form-data',
                }}
            }).then((request) => {
                this.n_array = request.data
            })
            this.getCount();
        },
        refresh: function(){
            if(this.n_counter == 0){
                this.getCount();
            }
        }
    },
    created () {
        this.getCount();
        setInterval(this.refresh, 2000);
    }
}

</script>


<template>
<div>

    <li class="nav-item dropdown" id="notification-dropdown">
        <a class="nav-link dropdown-toggle specialdropdown" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="padding-top: 0.2rem; padding-bottom: 0;">
            <i v-if="n_counter == 0" class="far fa-bell bell nav-link" style="padding-right: 0;"></i>
            <div v-else @click="getNotifications">
                <i class="fas fa-bell bell nav-link" style="padding-right: 0;"></i>
            </div>
        </a>
        <div id="modal-container" class="dropdown-menu dropdown-menu-right m-2" style="margin-top: 0.7rem !important">
            <form>
                <div v-if="n_counter != 0" class="place-for-notifications">
                    <div v-for="elem in n_array" :key="elem.key" class="alert alert-dismissible show border border-info rounded hoverable onemessage">
                        <a :href="elem.target">
                            <div>{{ elem.description }}</div>
                        </a>
                        <button type="button" class="close" aria-label="Close" @click="deleteOne(elem.key)">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                </div>
            </form>
            <form>
                <div v-if="n_counter != 0" class="deleteAllM">
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
    padding-top: 0;
    min-width: 350px;
}

.specialdropdown::after{
    content: none;
}

.dropdown-menu-right{
    right: -160px;
}

.bell{
    font-size: 32px;
    padding: 0;
}

#modal-container {
  max-height: 500px;
}

.onemessage {
    margin-bottom: 8px;
}

.onemessage:hover{
    background-color: #00709e12;
}

.onemessage a{
    color: #212529;
}

.place-for-notifications{
    max-height: 395px;
    overflow-y: scroll;
    padding-top: 8px;
    margin-left: 7px;
    padding-right: 5px;
}

.NoM {
    color: #9c9999;
    text-align: center;
    padding-bottom: 10px;
    padding-top: 10px;
    margin-top: 10px;
}

.deleteAllM {
    width: 100%;
    text-align: center;
    padding-top: 10px;
    border-top: 1px solid #00000021;
}

</style>