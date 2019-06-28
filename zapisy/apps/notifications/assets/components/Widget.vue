<script lang="ts">
import Vue from "vue";
import axios, { AxiosProxyConfig, AxiosPromise } from 'axios';
import Component from "vue-class-component";

interface NotificationsArray {
    id: string;
    description: string;
    issued_on: string;
    target: string;
}

interface NotificationsDict {
    [key: string]: NotificationsArray;
}

interface ServerResponseDict {
    data: NotificationsDict;
}

interface ServerResponseCount {
    data: number;
}


@Component
export default class NotificationsComponent extends Vue{

    n_counter: number|null = null;
    n_list: NotificationsDict = {};

    getCount(): Promise<number> {
        return axios.get('/notifications/count')
        .then((result: ServerResponseCount) => {
            return result.data
        })
    }

    async updateCounter(): Promise<void>{
        this.n_counter = await this.getCount();
    }

    getNotifications(): Promise<void> {
        return axios.get('/notifications/get')
        .then((result: ServerResponseDict) => {
            this.n_list = result.data
        })
    }

    async deleteAll(): Promise<void> {
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';

        return axios.post('/notifications/delete/all')
        .then((request: ServerResponseDict) => {
            this.n_list = request.data
            this.updateCounter();
        })
    }

    deleteOne(i: number): Promise<void> {
        axios.defaults.xsrfCookieName = 'csrftoken';
        axios.defaults.xsrfHeaderName = 'X-CSRFToken';

        var FormBody = new FormData();
        FormBody.append('issued_on', this.n_list[i].issued_on);
        FormBody.append('id', this.n_list[i].id);

       return axios.request({
            method: 'post',
            url: '/notifications/delete',
            data: FormBody,
            headers: {
                'Content-Type': 'multipart/form-data',
            }
        }).then((request: ServerResponseDict) => {
            this.n_list = request.data
            this.updateCounter();
        })
    }

    refresh(): void{
        if(this.n_counter === 0){
            this.updateCounter();
        }
    }

    async created() {
        console.log(this.n_counter)
        await this.updateCounter()
        console.log(this.n_counter)
        setInterval(this.refresh, 2000);
    }

}
</script>


<template>
<div>
    <li class="nav-item dropdown" id="notification-dropdown">
        <a class="nav-link dropdown-toggle specialdropdown" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false" style="padding-top: 0.2rem; padding-bottom: 0;">
            <div v-if="n_counter" @click="getNotifications()">
                <i class="fas fa-bell bell nav-link" style="padding-right: 0;"></i>
            </div>
            <div v-else>
               <i class="far fa-bell bell nav-link" style="padding-right: 0;"></i>
            </div>
        </a>
        <div id="modal-container" class="dropdown-menu dropdown-menu-right m-2" style="margin-top: 0.7rem !important">
            <form>
                <div v-if="n_counter" class="place-for-notifications">
                    <div v-for="elem in n_list" :key="elem.key" class="alert alert-dismissible show border border-info rounded hoverable onemessage">
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
                <div v-if="n_counter" class="deleteAllM">
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