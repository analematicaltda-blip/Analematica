# backend/apps/core_erp/views.py
import json
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.conf import settings

class SystemIntegrityStatusView(APIView):
    """
    Endpoint para visualizar el último reporte de certificación del sistema.
    """
    permission_classes = [IsAdminUser]

    def get(self, request):
        report_path = os.path.join(settings.BASE_DIR, "system_integrity_report.json")

        if not os.path.exists(report_path):
            return Response({
                "status": "NOT_CERTIFIED",
                "message": "No se ha ejecutado la certificación de integridad. Use 'python manage.py certify_system'."
            }, status=404)

        with open(report_path, "r") as f:
            report = json.load(f)

        return Response(report)

class RunCertificationView(APIView):
    """
    Dispara una nueva certificación de integridad.
    """
    permission_classes = [IsAdminUser]

    def post(self, request):
        from .integrity.system_integrity_certifier import SystemIntegrityCertifier
        certifier = SystemIntegrityCertifier()
        report = certifier.run_full_certification()
        return Response(report)
