from rest_framework.routers import DefaultRouter
from .views import DocumentoViewSet

router = DefaultRouter()
router.register(r'documentos', DocumentoViewSet)

urlpatterns = router.urls
</xai:function_call name="create_file">apps/desktop/renderer/src/dashboard/archive/ArchiveDashboard.tsx
<parameter name="content">import React from 'react';

const ArchiveDashboard = () => (
  <div>
    <h2>Archivo Mi Negocio</h2>
    <p>Upload/search/full-text ready (integrate with views).</p>
  </div>
);

export default ArchiveDashboard;

