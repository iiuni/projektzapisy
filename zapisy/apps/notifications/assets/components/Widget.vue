<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import axios, { AxiosProxyConfig, AxiosPromise } from 'axios';
import moment from 'moment'

interface Notifications {
    id: string;
    description: string;
    issued_on: string;
    target: string;
}

interface NotificationsDict {
    [key: string]: Notifications;
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

    n_list: NotificationsDict = {};

    get n_counter(): number {
        return Object.keys(this.n_list).length;
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
            this.n_list = request.data;
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
            this.n_list = request.data;
        })
    }

    async created() {
        this.getNotifications();
        setInterval(this.getNotifications, 30000);
    }

}
</script>


<template>
<div>
    <li id="notification-dropdown" class="nav-item dropdown">
        <a class="nav-link dropdown-toggle specialdropdown ml-1" href="#" id="navbarDropdown" role="button"
            data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
            <div v-if="n_counter !== 0">
                <font-awesome-icon :icon="['fas', 'bell']" size="lg" />
                <span class="counter-badge">{{ n_counter }}</span>
            </div>
            <div v-else>
               <font-awesome-icon :icon="['far', 'bell']" size="lg" />
            </div>
        </a>
        <div class="dropdown-menu dropdown-menu-right">
            <form class="p-1 place-for-notifications">
                <div v-for="elem in n_list" :key="elem.key" class="toast mb-1 show">
                    <div class="toast-header">
                        <strong class="mr-auto"></strong>
                        <small class="text-muted mx-2">{{ elem.issued_on|Moment }}</small>
                        <button type="button" class="close" @click="deleteOne(elem.key)">
                            &times;
                        </button>
                    </div>
                    <a :href="elem.target" class="toast-link">
                        <div class="toast-body text-body"
                        v-html="elem.description"></div>
                    </a>
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

<style lang="scss" scoped>
/*  Modification of the bootstrap class .dropdown-menu
    for display notifications widget correctly.  */
#notification-dropdown .dropdown-menu{
    @media (min-width: 992px) {
        min-width: 350px;
    }
    max-height: 500px;
    right: -160px;
}

/*  Hide arrow, what is default
    for tag <a> in .dropdown-menu  */
.specialdropdown::after{
    content: none;
}

a.toast-link:hover {
    text-decoration: none;
    .toast-body {
        background-color: var(--light);
    }
}

.place-for-notifications{
    max-height: 395px;
    overflow-y: auto;
}

.counter-badge {
    background-color: var(--pink);
    border-radius: 2px;
    color: white;
    font-weight: bold;
    
    padding: 1px 3px;

    // Bootstrap breakpoint at which the navbar is fully expanded.
    @media (min-width: 992px) {
        font-size: 10px;

        position: absolute; /* Position the badge within the relatively positioned button */
        top: 2px;
        right: 2px;
    }
    margin-left: .25em;
}

</style>
