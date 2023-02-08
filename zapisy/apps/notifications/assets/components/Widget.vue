<script lang="ts">
import { faBell as fasBell } from "@fortawesome/free-solid-svg-icons/faBell";
import { faBell as farBell } from "@fortawesome/free-regular-svg-icons/faBell";
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import Vue from "vue";
import Component from "vue-class-component";
import { Notification } from "../models";
import NotificationToast from "./NotificationToast.vue";
import NotificationRepository from "../repository";
import { NotificationsUpdateEvent } from "../events";

function truncateDescription(description: string) {
  if (description.length <= 200) return description;
  return description.substr(0, 200) + "...";
}

function truncateNotifications(notifications: Notification[]): Notification[] {
  return notifications.map((notification) => {
    notification.description = truncateDescription(notification.description);
    return notification;
  });
}

@Component({
  components: {
    FontAwesomeIcon,
    NotificationToast,
  },
})
export default class NotificationsComponent extends Vue {
  notifications: Notification[] = [];
  updateNotificationsEvent!: NotificationsUpdateEvent;

  get truncatedNotifications() {
    return truncateNotifications(this.notifications);
  }

  get n_counter(): number {
    return this.notifications.length;
  }

  farBell = farBell;
  fasBell = fasBell;

  async deleteAll() {
    let notifications = await NotificationRepository.deleteAll();
    this.updateNotificationsEvent.dispatch(notifications);
  }

  async created() {
    this.notifications = await NotificationRepository.getAll();
    setInterval(async () => {
      this.notifications = await NotificationRepository.getAll();
    }, 30000);

    this.updateNotificationsEvent = new NotificationsUpdateEvent();
    this.updateNotificationsEvent.subscribe(((event: CustomEvent) => {
      this.notifications = event.detail.notifications;
    }) as EventListener);
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
          <NotificationToast
            v-for="notification in notifications"
            :key="notification.id"
            :notification="notification"
          />
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
