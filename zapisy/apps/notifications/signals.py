from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse

from apps.notifications.datatypes import Notification
from apps.enrollment.courses.models.group import Group
from apps.news.models import News
from apps.notifications.api import notify_user, notify_selected_users
from apps.notifications.models import get_all_users_in_course_groups, get_all_users, get_all_students, get_all_users_from_group, get_enrolled_users_from_group, get_queued_users_from_group
from apps.notifications.custom_signals import teacher_changed
from apps.notifications.templates import NotificationType

from apps.news.views import all_news
from apps.enrollment.courses.views import course_view


@receiver(post_save, sender=Group)
def notify_that_group_was_added_in_course(sender: Group, **kwargs) -> None:
    group = kwargs['instance']
    if kwargs['created'] and group.course.information:
        course_groups = Group.objects.filter(course=group.course)
        course_name = group.course.information.entity.name

        teacher = group.teacher.user
        target = reverse(course_view, args=[group.course.slug])

        notify_user(
            teacher,
            Notification(NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
                         {'course_name': course_name}, target))

        users = get_all_users_in_course_groups(course_groups)
        notify_selected_users(
            users,
            Notification(NotificationType.ADDED_NEW_GROUP, {
                'course_name': course_name,
                'teacher': teacher.get_full_name()
            }, target))


@receiver(teacher_changed, sender=Group)
def notify_that_teacher_was_changed(sender: Group, **kwargs) -> None:
    group = kwargs['instance']

    teacher = group.teacher.user
    course_name = group.course.information.entity.name
    target = reverse(course_view, args=[group.course.slug])

    notify_user(
        teacher,
        Notification(NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
                     {'course_name': course_name}, target))

    queued_users = get_queued_users_from_group(group)
    enrolled_users = get_enrolled_users_from_group(group)

    notify_selected_users(
        queued_users,
        Notification(
            NotificationType.TEACHER_HAS_BEEN_CHANGED_QUEUED, {
                'course_name': course_name,
                'teacher': teacher.get_full_name(),
                'type': group.human_readable_type().lower()
            }, target))

    notify_selected_users(
        enrolled_users,
        Notification(
            NotificationType.TEACHER_HAS_BEEN_CHANGED_ENROLLED, {
                'course_name': course_name,
                'teacher': teacher.get_full_name(),
                'type': group.human_readable_type().lower()
            }, target))


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
