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
                <i class="fas fa-bell bell nav-link p-0"></i>
            </div>
            <div v-else>
               <i class="far fa-bell bell nav-link p-0"></i>
            </div>
        </a>
        <div class="dropdown-menu dropdown-menu-right m-2 pb-2 pt-0">
            <form>
                <div v-if="n_counter" class="place-for-notifications pt-2 ml-2 pr-2">
                    <div v-for="elem in n_list" :key="elem.key" class="alert alert-dismissible show border border-info rounded onemessage mb-2">
                        <a :href="elem.target" class="text-dark">
                            <div>{{ elem.description }}</div>
                        </a>
                        <button type="button" class="close" @click="deleteOne(elem.key)">
                            &times;
                        </button>
                    </div>
                </div>
            </form>
            <form>
                <div v-if="n_counter" class="pt-2 border-top text-center w-100">
                    <a href="#" @click="deleteAll">Usuń wszystkie powiadomienia.</a>
                </div>
                <div v-else class="text-center text-muted pb-2 pt-2 mt-2">
                    Brak nowych powiadomień.
                </div>
            </form>
        </div>
    </li>

</div>
</template>

<style>

/*  Modyfikacja bootstrapowej klasy .dropdown-menu na potrzeby
    wyświetlania widżetu z powiadomieniami  */
#notification-dropdown .dropdown-menu{
    min-width: 350px;
    max-height: 500px;
    right: -160px;
}

/*  Usunięcie strzałki, domyślnie widocznej
    przy tagu <a> w .dropdown-menu  */
.specialdropdown::after{
    content: none;
}

/*  Dopasowanie wielkości dzwonka  */
.bell{
    font-size: 24px;
}

/*  Zmiana koloru pojedynczego powiadomienia
    po najechaniu kursorem myszy  */
.onemessage:hover{
    background-color: #00709e12;
}

/*  Wymuszenie widoczności paska do scrollowania
    i określenie wysokości niescrollowanej części
    diva zawierającego powiadomienia  */
.place-for-notifications{
    max-height: 395px;
    overflow-y: scroll;
}

</style>