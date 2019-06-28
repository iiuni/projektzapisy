import django.dispatch

student_pulled = django.dispatch.Signal(providing_args=["instance", "user"])
student_not_pulled = django.dispatch.Signal(providing_args=["instance", "user", "reason"])
teacher_changed = django.dispatch.Signal(providing_args=["instance", "teacher"])
