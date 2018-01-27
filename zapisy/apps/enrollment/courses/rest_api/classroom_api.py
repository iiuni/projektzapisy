from rest_framework import serializers, viewsets
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from apps.users.utils import StaffPermission
from ..models.classroom import Classroom


class ClassroomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classroom
        fields = ('id', 'type', 'description', 'number', 'order', 'building', 'capacity',
                  'floor', 'can_reserve', 'slug')


class ClassroomViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    authentication_classes = (BasicAuthentication, SessionAuthentication)
    permission_classes = (StaffPermission,)
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer
