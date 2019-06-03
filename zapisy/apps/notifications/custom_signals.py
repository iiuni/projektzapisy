import django.dispatch

#student_not_pulled = django.dispatch.Signal(providing_args=["instance", "user"])
student_put_into_queue = django.dispatch.Signal(providing_args=["instance", "user"])
student_enrolled = django.dispatch.Signal(providing_args=["instance", "user"])
teacher_changed = django.dispatch.Signal(providing_args=["instance", "teacher"])
terms_changed = django.dispatch.Signal(providing_args=["instance"])
