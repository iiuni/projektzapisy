from apps.notifications.datatypes import CourseNotificationType, NewsNotificationType, ThesisNotificationType


mapping = {
    CourseNotificationType.NOT_PULLED_FROM_QUEUE:
    'Proces wciągania Cię do grupy przedmiotu "{course_name}", gdzie prowadzący to {teacher}, a '
    'typ grupy {type}, zakończył się niepowodzeniem. Powód: {reason}.',
    CourseNotificationType.PULLED_FROM_QUEUE:
    'Nastąpiło pomyślne zapisanie Cię do grupy przedmiotu "{course_name}", gdzie prowadzący grupy '
    'to {teacher}, a typ grupy to {type}.',
    CourseNotificationType.ADDED_NEW_GROUP:
    'W przedmiocie "{course_name}" została dodana grupa prowadzona przez {teacher}.',
    CourseNotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER:
    'Przydzielono Cię do grupy przedmiotu "{course_name}" jako prowadzącego.',
    CourseNotificationType.TEACHER_HAS_BEEN_CHANGED_ENROLLED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu "{course_name}", do której jesteś zapisany/a. '
    'Typ grupy to {type}, a nowy prowadzący to {teacher}.',
    CourseNotificationType.TEACHER_HAS_BEEN_CHANGED_QUEUED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu "{course_name}", do której jesteś w kolejce. '
    'Typ grupy to {type}, a nowy prowadzący to {teacher}.',
    NewsNotificationType.NEWS_HAS_BEEN_ADDED:
    "Dodano nową wiadomość w aktualnościach:\n# {title}\n\n{contents}",
    NewsNotificationType.NEWS_HAS_BEEN_ADDED_HIGH_PRIORITY:
    "Dodano nową wiadomość w aktualnościach:\n# {title}\n\n{contents}",
    ThesisNotificationType.THESIS_VOTING_HAS_BEEN_ACTIVATED:
    'W pracy dyplomowej "{title}" pojawiła się możliwość głosowania.',
}

mapping_title = {
    CourseNotificationType.NOT_PULLED_FROM_QUEUE:
    'Proces wciągania Cię do grupy zakończył się niepowodzeniem',
    CourseNotificationType.PULLED_FROM_QUEUE:
    'Nastąpiło pomyślne zapisanie Cię do grupy przedmiotu "{course_name}"',
    CourseNotificationType.ADDED_NEW_GROUP:
    'W przedmiocie "{course_name}" została dodana grupa',
    CourseNotificationType.ASSIGNED_TO_NEW_GROUP_AS_A_TEACHER:
    'Przydzielono Cię do grupy przedmiotu "{course_name}"',
    CourseNotificationType.TEACHER_HAS_BEEN_CHANGED_ENROLLED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu "{course_name}"',
    CourseNotificationType.TEACHER_HAS_BEEN_CHANGED_QUEUED:
    'Nastąpiła zmiana prowadzacego w grupie przedmiotu "{course_name}"',
    NewsNotificationType.NEWS_HAS_BEEN_ADDED:
    "{title}",
    NewsNotificationType.NEWS_HAS_BEEN_ADDED_HIGH_PRIORITY:
    "{title}",
    ThesisNotificationType.THESIS_VOTING_HAS_BEEN_ACTIVATED:
    'W pracy dyplomowej "{title}" pojawiła się możliwość głosowania.',
}
