<script lang="ts">
import { faBell as fasBell } from "@fortawesome/free-solid-svg-icons/faBell";
import { faBell as farBell } from "@fortawesome/free-regular-svg-icons/faBell";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import "dayjs/locale/pl";
import Vue from "vue";
import Component from "vue-class-component";
import { mapState } from "vuex";

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale("pl");

@Component({
  components: {
    FontAwesomeIcon,
  },
  computed: {
    ...mapState("notifications", {
      notifications: "notifications",
    }),
  },
  filters: {
    Moment: function (str: string) {
      return dayjs.tz(str, "Europe/Warsaw").fromNow();
    },
  },
})
export default class NotificationsComponent extends Vue {
  get n_counter(): number {
    return this.notifications.length;
  }

  farBell = farBell;
  fasBell = fasBell;

  deleteAll() {
    this.$store.dispatch("notifications/deleteAll");
  }

  deleteOne(id: string) {
    this.$store.dispatch("notifications/delete", id);
  }

  created() {
    this.$store.dispatch("notifications/get");
    setInterval(() => this.$store.dispatch("notifications/get"), 30000);
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
          <div
            v-for="elem in notifications"
            :key="elem.id"
            class="toast mb-1 show"
          >
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
