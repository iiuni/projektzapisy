from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from apps.notifications.datatypes import Notification
from apps.enrollment.courses.models.group import Group
from apps.news.models import News
from apps.notifications.api import notify_user, notify_selected_users
from apps.notifications.models import get_all_users_in_course_groups, get_all_users, get_all_students
from apps.notifications.custom_signals import teacher_changed
from apps.notifications.templates import NotificationType

from apps.news.views import all_news


@receiver(post_save, sender=Group)
def notify_that_group_was_added_in_course(sender: Group, **kwargs) -> None:
    group = kwargs['instance']
    if kwargs['created'] and group.course.information:
        course_groups = Group.objects.filter(course=group.course)
        course_name = group.course.information.entity.name

        teacher = group.teacher.user
        notify_user(
            teacher,
            Notification(NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
                         {'course_name': course_name}))

        users = get_all_users_in_course_groups(course_groups)
        notify_selected_users(
            users,
            Notification(NotificationType.ADDED_NEW_GROUP, {
                'course_name': course_name,
                'teacher': teacher.get_full_name()
            }))


@receiver(teacher_changed, sender=Group)
def notify_that_teacher_was_changed(sender: Group, **kwargs) -> None:
    group = kwargs['instance']

    teacher = group.teacher.user
    course_name = group.course.information.entity.name

    notify_user(
        teacher,
        Notification(NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
                     {'course_name': course_name}))

    users = get_all_users_in_course_groups([group])
    notify_selected_users(
        users,
        Notification(
            NotificationType.TEACHER_HAS_BEEN_CHANGED, {
                'course_name': course_name,
                'teacher': teacher.get_full_name(),
                'type': group.human_readable_type().lower()
            }))


@receiver(post_save, sender=News)
def notify_that_news_was_added(sender: News, **kwargs) -> None:
    news = kwargs['instance']

    users = get_all_users()
    target = reverse(all_news)

    notify_selected_users(
        users,
        Notification(
            NotificationType.NEWS_HAS_BEEN_ADDED, {}, target
        ))
