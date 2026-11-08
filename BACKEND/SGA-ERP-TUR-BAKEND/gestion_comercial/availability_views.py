from django.conf import settings
from rest_framework.response import Response
from rest_framework.exceptions import APIException

class CapacityUnavailable(APIException):
    status_code=503
    default_detail='La gestión de cupos no está habilitada en este entorno.'
    default_code='capacity_disabled'
from rest_framework.exceptions import ValidationError
from .quote_views import PrivateDraftView
from .availability import availability,create_hold,release_hold,present

class CapacityView(PrivateDraftView):
    def initial(self,request,*args,**kwargs):
        super().initial(request,*args,**kwargs)
        if not getattr(settings,'ERP_CAPACITY_HOLDS_ENABLED',False):raise CapacityUnavailable()

class ServiceAvailability(CapacityView):
    def post(self,request):return Response(availability(request.user,request.data))

class CapacityHoldCreate(CapacityView):
    def post(self,request):
        hold,created=create_hold(request.user,request.data)
        return Response(present(hold),status=201 if created else 200)

class CapacityHoldRelease(CapacityView):
    def post(self,request,pk):
        if request.data!={}:raise ValidationError('La liberación no admite campos adicionales.')
        return Response(present(release_hold(request.user,pk)))
