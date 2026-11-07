from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied
from .services.gestion_plataforma_service import GestionPlataformaService
from .services.governance_kernel import GovernanceKernel

class SystemicERPViewSetMixin:
    """
    Mixin para asegurar que los ViewSets del Admin de Plataforma
 
    siempre filtren por el perfil de la organización central (Gobierno)
    dentro del dominio administrativo instanciado.
    """
    def get_queryset(self):
        perfil_gobierno = GestionPlataformaService.get_perfil_gobierno_context()
 
        queryset = super().get_queryset()

        if not perfil_gobierno:
            return queryset

 
        # En el dominio instanciado usamos 'organization' por defecto
        if hasattr(queryset.model, 'organization'):
            return queryset.filter(organization=perfil_gobierno)

        # Fallbacks para otros esquemas si existieran
 
        if hasattr(queryset.model, 'provider'):
            return queryset.filter(provider=perfil_gobierno)
        elif hasattr(queryset.model, 'perfil'):
            return queryset.filter(perfil=perfil_gobierno)
 

        return queryset

    def perform_create(self, serializer):
        self._check_governance_block('CREATE')
        super().perform_create(serializer)

    def perform_update(self, serializer):
        self._check_governance_block('UPDATE')
        super().perform_update(serializer)

    def perform_destroy(self, instance):
        self._check_governance_block('DELETE')
        super().perform_destroy(instance)

    def _check_governance_block(self, action_type: str):
        """
        Consulta al Kernel si existe un bloqueo soberano para el dominio actual.
        """
        # Intentar determinar el dominio basado en el app_label del modelo
        model = self.get_queryset().model
        domain = getattr(model._meta, 'app_label', 'unknown')

        # El Kernel evalúa si hay políticas BLOCK activas para este dominio
        from .services.governance_kernel import GovernanceKernel, AuthorityLevel
        kernel = GovernanceKernel(user=self.request.user)

        # Verificación rápida de bloqueos de dominio (intención genérica ficticia para validación)
        try:
             kernel._evaluate_policies(
                 intention=type('Intention', (), {'domain': domain, 'name': f'ERP_{action_type}'}),
                 parameters={}
             )
        except Exception as e:
            raise PermissionDenied(detail=str(e))
