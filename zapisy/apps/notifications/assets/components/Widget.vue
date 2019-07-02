<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import axios, { AxiosProxyConfig, AxiosPromise } from 'axios';
import moment from 'moment'

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


@Component({
    filters: {
        Moment: function(str: string) {
    	    return moment(str).locale('pl').fromNow();
        }
    }
})
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

    deleteAll(): Promise<void> {
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
        if(this.n_counter){}
        else{
            this.updateCounter();
        }
    }

    async created() {
        await this.updateCounter()
        setInterval(this.refresh, 2000);
    }

}
</script>


<template>
<div>
    <li id="notification-dropdown" class="nav-item dropdown">
        <a class="nav-link dropdown-toggle specialdropdown ml-1" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <div v-if="n_counter" @click="getNotifications()">
                <i class="fas fa-bell fa-lg"></i>
            </div>
            <div v-else>
               <i class="far fa-bell fa-lg"></i>
            </div>
        </a>
        <div class="dropdown-menu dropdown-menu-right m-2 pb-2 pt-0">
            <form class="p-2 place-for-notifications">
                <div v-for="elem in n_list" :key="elem.key" class="toast fade show mw-100 mb-2">
                    <div class="toast-header">
                        <strong class="mr-auto"></strong>
                        <small class="text-muted">{{ elem.issued_on|Moment }}</small>
                        <button type="button" class="ml-2 mb-1 close" @click="deleteOne(elem.key)">
                            &times;
                        </button>
                    </div>
                    <div class="toast-body">
                        <a :href="elem.target" class="text-body">{{ elem.description }}</a>
                    </div>
                </div>
            </form>
            <form>
                <div v-if="n_counter" class="pt-2 border-top text-center w-100">
                    <a href="#" @click="deleteAll">Usuń wszystkie powiadomienia.</a>
                </div>
                <div v-else class="text-center text-muted pb-2 pt-1">
                    Brak nowych powiadomień.
                </div>
            </form>
        </div>
    </li>

</div>
</template>

<style>

/*  Modification of the bootstrap class .dropdown-menu
    for display notifications widget correctly.  */
#notification-dropdown .dropdown-menu{
    min-width: 350px;
    max-height: 500px;
    right: -160px;
}

/*  Hide arrow, what is default
    for tag <a> in .dropdown-menu  */
.specialdropdown::after{
    content: none;
}

.place-for-notifications{
    max-height: 395px;
    overflow-y: auto;
}

</style>
