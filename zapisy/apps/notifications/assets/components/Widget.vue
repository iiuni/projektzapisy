<script lang="ts">
import { faBell as fasBell } from "@fortawesome/free-solid-svg-icons/faBell";
import { faBell as farBell } from "@fortawesome/free-regular-svg-icons/faBell";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import axios from "axios";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import "dayjs/locale/pl";
import { parse, ParseFn, fromMap, aString, anArrayContaining } from "spicery";
import Vue from "vue";
import Component from "vue-class-component";

class Notification {
  constructor(
    public id: string,
    public description: string,
    public issuedOn: string,
    public target: string
  ) {}
}

// Defines a parser that validates and parses Notifications from JSON.
const notifications: ParseFn<Notification> = (x: any) =>
  new Notification(
    fromMap(x, "id", aString),
    fromMap(x, "description", aString),
    fromMap(x, "issued_on", aString),
    fromMap(x, "target", aString)
  );
const notificationsArray = anArrayContaining(notifications);

dayjs.extend(relativeTime);
dayjs.locale("pl");

@Component({
  components: {
    FontAwesomeIcon,
  },
  filters: {
    Moment: function (str: string) {
      return dayjs(str).fromNow();
    },
  },
})
export default class NotificationsComponent extends Vue {
  n_list: Notification[] = [];

  get n_counter(): number {
    return this.n_list.length;
  }

  farBell = farBell;
  fasBell = fasBell;

  getNotifications() {
    return axios
      .get("/notifications/get")
      .then((r) => parse(notificationsArray)(r.data))
      .then((t) => {
        this.n_list = t;
      });
  }

  deleteAll(): Promise<void> {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";

    return axios
      .post("/notifications/delete/all")
      .then((r) => parse(notificationsArray)(r.data))
      .then((t) => {
        this.n_list = t;
      });
  }

  deleteOne(i: number): Promise<void> {
    axios.defaults.xsrfCookieName = "csrftoken";
    axios.defaults.xsrfHeaderName = "X-CSRFToken";

    return axios
      .post("/notifications/delete", {
        uuid: i,
      })
      .then((r) => parse(notificationsArray)(r.data))
      .then((t) => {
        this.n_list = t;
      });
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
      <a
        class="nav-link dropdown-toggle specialdropdown ml-1"
        href="#"
        id="navbarDropdown"
        role="button"
        data-toggle="dropdown"
        aria-haspopup="true"
        aria-expanded="false"
      >
        <div v-if="n_counter !== 0">
          <font-awesome-icon :icon="fasBell" size="lg" />
          <span class="counter-badge">{{ n_counter }}</span>
        </div>
        <div v-else>
          <font-awesome-icon :icon="farBell" size="lg" />
        </div>
      </a>
      <div class="dropdown-menu dropdown-menu-right">
        <form class="p-1 place-for-notifications">
          <div v-for="elem in n_list" :key="elem.id" class="toast mb-1 show">
            <div class="toast-header">
              <strong class="mr-auto"></strong>
              <small class="text-muted mx-2">{{
                elem.issuedOn | Moment
              }}</small>
              <button type="button" class="close" @click="deleteOne(elem.id)">
                &times;
              </button>
            </div>
            <a :href="elem.target" class="toast-link">
              <div class="toast-body text-body">{{ elem.description }}</div>
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
// Modifies the bootstrap class .dropdown-menu display notifications widget
// correctly.
#notification-dropdown .dropdown-menu {
  @media (min-width: 992px) {
    min-width: 350px;
  }
  max-height: 500px;
  right: -160px;
}

// Hide arrow, displayed by default for tag <a> in .dropdown-menu.
.specialdropdown::after {
  content: none;
}

a.toast-link:hover {
  text-decoration: none;
  .toast-body {
    background-color: var(--light);
  }
}

.toast-body {
  white-space: pre-wrap;
}

.place-for-notifications {
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

    position: absolute; // Position the badge within the relatively positioned button.
    top: 2px;
    right: 2px;
  }
  margin-left: 0.25em;
}
</style>
