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
        deleteOne: function (id){
            axios.defaults.xsrfCookieName = 'csrftoken';
            axios.defaults.xsrfHeaderName = 'X-CSRFToken';

            var FormBody = new FormData();
            FormBody.append('issued_on', this.n_array[id].issued_on);

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
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <svg v-if="n_counter == 0" aria-hidden="true" focusable="false" data-prefix="far" data-icon="bell" class="bell nav-link" style="padding-right: 0;" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path fill="currentColor" d="M439.39 362.29c-19.32-20.76-55.47-51.99-55.47-154.29 0-77.7-54.48-139.9-127.94-155.16V32c0-17.67-14.32-32-31.98-32s-31.98 14.33-31.98 32v20.84C118.56 68.1 64.08 130.3 64.08 208c0 102.3-36.15 133.53-55.47 154.29-6 6.45-8.66 14.16-8.61 21.71.11 16.4 12.98 32 32.1 32h383.8c19.12 0 32-15.6 32.1-32 .05-7.55-2.61-15.27-8.61-21.71zM67.53 368c21.22-27.97 44.42-74.33 44.53-159.42 0-.2-.06-.38-.06-.58 0-61.86 50.14-112 112-112s112 50.14 112 112c0 .2-.06.38-.06.58.11 85.1 23.31 131.46 44.53 159.42H67.53zM224 512c35.32 0 63.97-28.65 63.97-64H160.03c0 35.35 28.65 64 63.97 64z"></path>
            </svg>
            <svg v-else @click="getNotifications" aria-hidden="true" focusable="false" data-prefix="fas" data-icon="bell" class="bell nav-link" style="padding-right: 0;" role="img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 448 512">
                <path fill="currentColor" d="M224 512c35.32 0 63.97-28.65 63.97-64H160.03c0 35.35 28.65 64 63.97 64zm215.39-149.71c-19.32-20.76-55.47-51.99-55.47-154.29 0-77.7-54.48-139.9-127.94-155.16V32c0-17.67-14.32-32-31.98-32s-31.98 14.33-31.98 32v20.84C118.56 68.1 64.08 130.3 64.08 208c0 102.3-36.15 133.53-55.47 154.29-6 6.45-8.66 14.16-8.61 21.71.11 16.4 12.98 32 32.1 32h383.8c19.12 0 32-15.6 32.1-32 .05-7.55-2.61-15.27-8.61-21.71z"></path>
            </svg>
        </a>
        <div id="modal-container" class="dropdown-menu dropdown-menu-right m-2">
            <form>
                <p>Lista powiadomień:</p>
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
    padding-top: 8px;
    min-width: 350px;
}
.specialdropdown::after{
    content: none;
}
.dropdown-menu-right{
    right: -160px;
}
.bell{
    height: 23px;
    padding: 0;
}
#modal-container {
  max-height: 500px;
}

#modal-container p {
    display: block;
    width: 100%;
    font-size: 18px;
    color: #00709e;
    font-weight: bold;
    margin-bottom: 8px;
    margin-left: 8px;
}

.onemessage {
    margin-bottom: 10px;
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
    margin-left: 7px;
    padding-right: 5px;
}

.NoM {
    color: #9c9999;
    text-align: center;
    padding-bottom: 10px;
    padding-top: 10px;
}

.deleteAllM {
    width: 100%;
    text-align: center;
    padding-top: 10px;
    border-top: 1px solid #00000021;
}

</style>