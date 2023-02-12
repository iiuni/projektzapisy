<script lang="ts">
import Component from "vue-class-component";
import Vue from "vue";
import NotificationToast from "./NotificationToast.vue";
import { Notification, CourseTargetInfo } from "../models";
import { NotificationsUpdateEvent } from "../events";
import NotificationRepository from "../repository";

@Component({
  components: {
    NotificationToast,
  },
  props: ["courseId"],
})
export default class CourseNotifications extends Vue {
  notifications: Notification[] = [];
  notificationRepository!: NotificationRepository;
  notificationsUpdateEvent!: NotificationsUpdateEvent;
  limit = 1;

  get courseRelatedNotifications() {
    return this.notifications.filter((notification) => {
      if (notification.targetInfo instanceof CourseTargetInfo)
        return notification.targetInfo.courseId == this.$props.courseId;
      return false;
    });
  }

  get numberOfCourseNotifications() {
    return this.courseRelatedNotifications.length;
  }

  async created() {
    this.notificationRepository = new NotificationRepository();

    this.notificationsUpdateEvent = new NotificationsUpdateEvent();
    this.notificationsUpdateEvent.subscribe((notifications) => {
      this.notifications = notifications;
    });

    let notifications = await this.notificationRepository.getAll();
    this.notificationsUpdateEvent.dispatch(notifications);
  }
}
</script>

<template>
  <div class="mb-3" v-if="numberOfCourseNotifications">
    <div class="course-notification-list">
      <NotificationToast
        v-for="notification in courseRelatedNotifications.slice(0, limit)"
        :key="notification.id"
        :notification="notification"
        :clickable="false"
        class="course-notification-toast"
      />
    </div>
    <div class="pt-1 text-center" v-if="numberOfCourseNotifications > limit">
      <a href="#" @click.prevent="limit += 5">Pokaż więcej</a>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.course-notification-list {
  .course-notification-toast {
    box-shadow: none;
    max-width: none;
  }
}
</style>
