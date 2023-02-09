import CourseNotifications from "./components/CourseNotifications.vue";

const mountElementId = "#notifications-course";
const mountElement = document.querySelector(mountElementId);

new CourseNotifications({
  el: mountElementId,
  propsData: { ...mountElement.dataset },
});
