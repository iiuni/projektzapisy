from rest_framework import routers

from .views import (ClassroomViewSet, DesiderataOtherViewSet,
                    DesiderataViewSet, EmployeeViewSet, SemesterViewSet,
                    SpecialReservationViewSet, SystemStateViewSet,
                    SingleVoteViewSet)

router = routers.DefaultRouter()
router.register(r'semesters', SemesterViewSet)
router.register(r'classrooms', ClassroomViewSet)
router.register(r'employees', EmployeeViewSet)
router.register(r'desideratas', DesiderataViewSet)
router.register(r'desiderata-others', DesiderataOtherViewSet)
router.register(r'special-reservation', SpecialReservationViewSet)
router.register(r'systemstate', SystemStateViewSet)
router.register(r'votes', SingleVoteViewSet, 'Votes')
