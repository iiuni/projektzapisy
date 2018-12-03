from typing import Dict

from django.contrib.auth.models import User

from apps.notifications2.api import notify_user


def notify_that_user_was_pulled_from_queue(user: User, group) -> None:
    group_types: Dict = {"1": "wykład", "2": "ćwiczenia", "3": "pracownia", "5": "ćwiczenio-pracownia",
                         "6": "seminarium", "7": "lektorat", "8": "WF", "9": "repetytorium", "10": "projekt"}

    notify_user(user, "pulled_from_queue", {
        "course_name": group.course.information.entity.name,
        "teacher": group.teacher.user.get_full_name(),
        "type": group_types[group.type]
    })
