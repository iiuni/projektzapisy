<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import utc from "dayjs/plugin/utc";
import timezone from "dayjs/plugin/timezone";
import "dayjs/locale/pl";
import { Notification } from "../store/notifications";

dayjs.extend(relativeTime);
dayjs.extend(utc);
dayjs.extend(timezone);
dayjs.locale("pl");

const NotificationToastProps = Vue.extend({
  props: {
    notification: Notification,
  },
});

@Component({
  filters: {
    Moment: function (str: string) {
      return dayjs.tz(str, "Europe/Warsaw").fromNow();
    },
  },
})
export default class NotificationToast extends NotificationToastProps {
  deleteOne(id: string) {
    this.$store.dispatch("notifications/delete", id);
  }
}
</script>

<template>
  <div class="toast mb-1 show">
    <div class="toast-header">
      <strong class="mr-auto"></strong>
      <small class="text-muted mx-2">{{
        notification.issuedOn | Moment
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
