from rest_framework import serializers, viewsets

from ..models.semester import Semester


class SemesterSerializer(serializers.ModelSerializer):
    display_name = serializers.SerializerMethodField()

    class Meta:
        model = Semester
        fields = ('id', 'display_name')

    def get_display_name(self, obj):
        return obj.get_name()


class SemesterViewSet(viewsets.ModelViewSet):
    http_method_names = ['get']
    queryset = Semester.objects.order_by('-semester_beginning')
    serializer_class = SemesterSerializer
