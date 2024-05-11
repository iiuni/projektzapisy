import django.dispatch

# Signal senders must provide `instance` and `user` arguments.
#   instance: apps.enrollment.courses.models.Group
#   user: django.contrib.auth.models.User
student_pulled = django.dispatch.Signal()
# Signal senders must provide the following arguments:
#   instance: apps.enrollment.courses.models.Group
#   user: django.contrib.auth.models.User
#   reason: str
student_not_pulled = django.dispatch.Signal()
# Signal senders must provide the following arguments:
#   instance: apps.enrollment.courses.models.Group
#   teacher: apps.users.models.Employee
teacher_changed = django.dispatch.Signal()
# Signal senders must provide an argument:
#   instance: apps.theses.models.Thesis
thesis_voting_activated = django.dispatch.Signal()
