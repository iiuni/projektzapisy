from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
import uuid
from datetime import datetime

from apps.notifications.datatypes import Notification
from apps.enrollment.courses.models.group import Group
from apps.enrollment.records.models import Record
from apps.news.models import News
from apps.notifications.api import notify_user, notify_selected_users
from apps.notifications.models import get_all_users_in_course_groups, get_all_users, get_all_students, get_all_users_from_group, get_enrolled_users_from_group, get_queued_users_from_group
from apps.notifications.custom_signals import teacher_changed, terms_changed, student_enrolled
from apps.notifications.templates import NotificationType

from apps.news.views import all_news
from apps.enrollment.courses.views import course_view


@receiver(student_enrolled, sender=Record)
def notify_that_student_was_enrolled(sender: Record, **kwargs) -> None:
    group = kwargs['instance']
    target = reverse(course_view, args=[group.course.slug])

    notify_user(
        kwargs['user'],
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.STUDENT_HAS_BEEN_ENROLLED, {
                'course_name': group.course.information.entity.name,
                'teacher': group.teacher.user.get_full_name(),
                'type': group.human_readable_type().lower()
            }, target))


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
            Notification(str(uuid.uuid1()), datetime.now(),
                NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
                         {'course_name': course_name}, target))

        users = get_all_users_in_course_groups(course_groups)
        notify_selected_users(
            users,
            Notification(str(uuid.uuid1()), datetime.now(),
                NotificationType.ADDED_NEW_GROUP, {
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
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER,
                     {'course_name': course_name}, target))

    queued_users = get_queued_users_from_group(group)
    enrolled_users = get_enrolled_users_from_group(group)

    notify_selected_users(
        queued_users,
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.TEACHER_HAS_BEEN_CHANGED_QUEUED, {
                'course_name': course_name,
                'teacher': teacher.get_full_name(),
                'type': group.human_readable_type().lower()
            }, target))

    notify_selected_users(
        enrolled_users,
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.TEACHER_HAS_BEEN_CHANGED_ENROLLED, {
                'course_name': course_name,
                'teacher': teacher.get_full_name(),
                'type': group.human_readable_type().lower()
            }, target))


@receiver(terms_changed, sender=Group)
def notify_that_terms_of_group_were_changed(sender: Group, **kwargs) -> None:
    group = kwargs['instance']

    course_name = group.course.information.entity.name
    target = reverse(course_view, args=[group.course.slug])

    queued_users = get_queued_users_from_group(group)
    enrolled_users = get_enrolled_users_from_group(group)

    notify_selected_users(
        queued_users,
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.TERMS_HAVE_BEEN_CHANGED_QUEUED, {
                'course_name': course_name,
            }, target))

    notify_selected_users(
        enrolled_users,
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.TERMS_HAVE_BEEN_CHANGED_ENROLLED, {
                'course_name': course_name,
            }, target))


@receiver(post_save, sender=News)
def notify_that_news_was_added(sender: News, **kwargs) -> None:
    news = kwargs['instance']

    users = get_all_users()
    target = reverse(all_news)

    notify_selected_users(
        users,
        Notification(str(uuid.uuid1()), datetime.now(),
            NotificationType.NEWS_HAS_BEEN_ADDED, {}, target
        ))
