from enum import Enum


class NotificationType(str, Enum):
    NOT_PULLED_FROM_QUEUE = 'not_pulled_from_queue'
    PULLED_FROM_QUEUE = 'pulled_from_queue'
    ADDED_NEW_GROUP = 'added_new_group'
    ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER = 'assigned_to_new_group_as_teacher'
    TEACHER_HAS_BEEN_CHANGED_ENROLLED = 'teacher_has_been_changed_enrolled'
    TEACHER_HAS_BEEN_CHANGED_QUEUED = 'teacher_has_been_changed_queued'
    NEWS_HAS_BEEN_ADDED = 'news_has_been_added'


mapping = {
    NotificationType.NOT_PULLED_FROM_QUEUE:
    'Proces wciągania Cię do grupy przedmiotu "{course_name}", gdzie prowadzący to {teacher}, a '
    'typ grupy {type}, zakończył się niepowodzeniem. Powód: {reason}.',
    NotificationType.PULLED_FROM_QUEUE:
    'Nastąpiło pomyślne zapisanie Cię do grupy przedmiotu "{course_name}", gdzie prowadzący grupy '
    'to {teacher}, a typ grupy to {type}.',
    NotificationType.ADDED_NEW_GROUP:
    'W przedmiocie "{course_name}" została dodana grupa prowadzona przez {teacher}.',
    NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER:
    'Przydzielono Cię do grupy przedmiotu "{course_name}" jako prowadzącego.',
    NotificationType.TEACHER_HAS_BEEN_CHANGED_ENROLLED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu "{course_name}", do której jesteś zapisany/a. '
    'Typ grupy to {type}, a nowy prowadzący to {teacher}.',
    NotificationType.TEACHER_HAS_BEEN_CHANGED_QUEUED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu "{course_name}", do której jesteś w kolejce. '
    'Typ grupy to {type}, a nowy prowadzący to {teacher}.',
    NotificationType.NEWS_HAS_BEEN_ADDED:
    "Dodano nową wiadomość w aktualnościach: {title}\n"
    "{contents}",
}
