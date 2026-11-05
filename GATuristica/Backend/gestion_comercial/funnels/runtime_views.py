# funnels/runtime_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404

from .runtime.engine import process_event
from .runtime_models import Lead, LeadState

class FunnelEventView(APIView):
    """
    Endpoint público para recibir eventos de ejecución de embudos.
    No requiere autenticación.
    """
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        publication_slug = request.data.get('publication_slug')
        event_type = request.data.get('event_type')
        payload = request.data.get('payload', {})

        if not all([publication_slug, event_type]):
            return Response(
                {"error": "'publication_slug' and 'event_type' are required fields."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            lead = process_event(
                publication_slug=publication_slug,
                event_type=event_type,
                payload=payload
            )

            if lead:
                return Response({"status": "Event processed successfully.", "lead_id": lead.id}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"status": "Event received."}, status=status.HTTP_202_ACCEPTED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Captura de errores inesperados del motor
            return Response({"error": f"An internal error occurred: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LeadDetailView(APIView):
    """
    Endpoint para consultar el estado de un Lead.
    Requiere autenticación para uso interno.
    """
    def get(self, request, lead_id, *args, **kwargs):
        # Asegurarse de que el lead pertenece al tenant del usuario
        lead = get_object_or_404(Lead, id=lead_id, tenant=request.user.tenant)

        # Podríamos usar un serializador, pero para una vista simple, un diccionario es suficiente.
        data = {
            "id": str(lead.id),
            "funnel_id": lead.funnel_id,
            "form_data": lead.form_data,
            "created_at": lead.created_at,
            "state": {
                "current_page_id": lead.state.current_page_id,
                "status": lead.state.current_status,
                "updated_at": lead.state.updated_at
            }
        }
        return Response(data)
