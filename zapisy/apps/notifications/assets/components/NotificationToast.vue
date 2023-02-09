<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import "dayjs/locale/pl";
import { Notification } from "../models";
import { NotificationsUpdateEvent } from "../events";
import NotificationRepository from "../repository";

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.locale("pl");

const NotificationToastProps = Vue.extend({
  props: {
    notification: Notification,
  },
});

@Component
export default class NotificationToast extends NotificationToastProps {
  updateNotificationsEvent!: NotificationsUpdateEvent;
  notificationRepository!: NotificationRepository;

  async deleteOne(id: string) {
    let notifications = await this.notificationRepository.delete(id);
    this.updateNotificationsEvent.dispatch(notifications);
  }

  momentFromDate(date: Date) {
    return dayjs(date).fromNow();
  }

  created() {
    this.notificationRepository = new NotificationRepository();
    this.updateNotificationsEvent = new NotificationsUpdateEvent();
  }
}
</script>

<template>
  <div class="toast mb-1 show">
    <div class="toast-header">
      <strong class="mr-auto"></strong>
      <small class="text-muted mx-2">{{
        momentFromDate(notification.issuedOn)
      }}</small>
      <button type="button" class="close" @click="deleteOne(notification.id)">
        &times;
      </button>
    </div>
    <a :href="notification.target" class="toast-link">
      <div class="toast-body text-body">{{ notification.description }}</div>
    </a>
  </div>
</template>

<style lang="scss" scoped>
a.toast-link:hover {
  text-decoration: none;
  .toast-body {
    background-color: var(--light);
  }
}

.toast-body {
  white-space: pre-wrap;
}
</style>
