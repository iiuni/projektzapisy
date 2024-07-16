<script setup lang="ts">
import { faBell as fasBell } from "@fortawesome/free-solid-svg-icons/faBell";
import { faBell as farBell } from "@fortawesome/free-regular-svg-icons/faBell";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import axios from "axios";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import "dayjs/locale/pl";
import { z } from "zod";
import { ref, computed } from "vue";

// TODO czy klikniecie w powiadomienie nie powinno je odznaczac?

// Defines a notification scheme to validate and parse Notifications from JSON.
const notificationScheme = z
  .object({
    id: z.string(),
    description: z.string(),
    issued_on: z.string(),
    target: z.string(),
  })
  .transform((parsedObject) => {
    return {
      id: parsedObject.id,
      description: parsedObject.description,
      issuedOn: parsedObject.issued_on,
      target: parsedObject.target,
    };
  });

const notificationSchemeArray = z.array(notificationScheme);

type Notification = z.infer<typeof notificationScheme>;

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale("pl");

const Moment = (str: string) => {
  return dayjs.tz(str, "Europe/Warsaw").fromNow();
};

const n_list = ref<Notification[]>([]);
const n_counter = computed(() => n_list.value.length);

function getNotifications() {
  return axios
    .get("/notifications/get")
    .then((r) => notificationSchemeArray.parse(r.data))
    .then((t) => {
      n_list.value = t;
    });
}

function deleteAll(): Promise<void> {
  axios.defaults.xsrfCookieName = "csrftoken";
  axios.defaults.xsrfHeaderName = "X-CSRFToken";

  return axios
    .post("/notifications/delete/all")
    .then((r) => notificationSchemeArray.parse(r.data))
    .then((t) => {
      n_list.value = t;
    });
}

function deleteOne(i: number): Promise<void> {
  axios.defaults.xsrfCookieName = "csrftoken";
  axios.defaults.xsrfHeaderName = "X-CSRFToken";

  return axios
    .post("/notifications/delete", {
      uuid: i,
    })
    .then((r) => notificationSchemeArray.parse(r.data))
    .then((t) => {
      n_list.value = t;
    });
}

const created = async () => {
  await getNotifications();
  setInterval(getNotifications, 30000);
};
// TODO czy na pewno tak to powino created wygladac
// + trzeba przetestowac
created();
</script>

<template>
  <div>
    <li id="notification-dropdown" class="nav-item dropdown">
      <a
        class="nav-link dropdown-toggle specialdropdown ms-1"
        href="#"
        id="navbarDropdown"
        role="button"
        data-bs-toggle="dropdown"
        data-bs-auto-close="outside"
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
      <div class="dropdown-menu dropdown-menu-end">
        <form class="p-1 place-for-notifications">
          <div v-for="elem in n_list" :key="elem.id" class="toast mb-1 show">
            <div class="toast-header">
              <strong class="me-auto"></strong>
              <small class="text-muted mx-2">
                {{ Moment(elem.issuedOn) }}</small
              >
              <button
                type="button"
                class="btn-close"
                @click="deleteOne(elem.id)"
              ></button>
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
    background-color: var(--bs-light);
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
  background-color: var(--bs-pink);
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
