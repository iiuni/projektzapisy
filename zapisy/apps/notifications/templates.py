from enum import Enum


class NotificationType(str, Enum):
    PULLED_FROM_QUEUE = 'pulled_from_queue'
    NOT_PULLED_FROM_QUEUE = 'not_pulled_from_queue'
    ADDED_NEW_GROUP = 'added_new_group'
    ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER = 'assigned_to_new_group_as_teacher'
    TEACHER_HAS_BEEN_CHANGED = 'teacher_has_been_changed'


mapping = {
    NotificationType.PULLED_FROM_QUEUE:
    'Nastąpiło wciągnięcie Cię do grupy przedmiotu {course_name}, gdzie prowadzący to {teacher} a '
    'typ grupy {type}.',
    NotificationType.NOT_PULLED_FROM_QUEUE:
    'Proces wciągania Cię do grupy przedmiotu {course_name}, gdzie prowadzący to {teacher} a '
    'typ grupy {type}, został anulowany, ze względu na przekroczenie limitu ECTS.',
    NotificationType.ADDED_NEW_GROUP:
    'W przedmiocie {course_name} została dodana grupa prowadzona przez {teacher}.',
    NotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER:
    'Przydzielono Cię do grupy przedmiotu {course_name} jako prowadzącego.',
    NotificationType.TEACHER_HAS_BEEN_CHANGED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu {course_name}, gdzie typ grupy to '
    '{type}, na {teacher}.',
}
