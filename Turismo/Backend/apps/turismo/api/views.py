from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .serializers import DepartmentSerializer, MunicipalitySerializer
from ..models.divipola import Department, Municipality

class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    filter_backends = [SearchFilter]
    search_fields = ['name']

class MunicipalityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Municipality.objects.all()
    serializer_class = MunicipalitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['dept']

    @action(detail=False, methods=['get'])
    def by_dept(self, request):
        dept_code = request.query_params.get('code')
        if dept_code:
            queryset = self.filter_queryset(self.get_queryset()).filter(dept__code=dept_code)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
        return Response([])

