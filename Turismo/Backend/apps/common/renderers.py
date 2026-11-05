from rest_framework.renderers import JSONRenderer

class EnterpriseJSONRenderer(JSONRenderer):
    """
    Fase 3: Enterprise API Contract Layer.
    Normaliza todas las respuestas de la API bajo un contrato estructural único.
    """
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        response = renderer_context.get('response')

        # Determinar éxito basado en el código de estado HTTP
        success = True
        if response and response.status_code >= 400:
            success = False

        # Extraer meta y errors si existen en los datos (usualmente inyectados por el exception handler)
        errors = data.get('errors', None) if isinstance(data, dict) else None
        meta = data.get('meta', {}) if isinstance(data, dict) else {}

        # Si es un error, el 'data' del contrato debe ser null
        # Si no, el 'data' es el payload original (quitando meta/errors si estaban ahí)
        final_data = data
        if not success:
            final_data = None
        elif isinstance(data, dict):
            # Si era una respuesta paginada de DRF, movemos la paginación a meta
            if 'results' in data and 'count' in data:
                meta.update({
                    'total': data.get('count'),
                    'next': data.get('next'),
                    'previous': data.get('previous'),
                })
                final_data = data.get('results')
            else:
                # Limpiar llaves reservadas si existen en el payload de éxito
                if 'meta' in data: data.pop('meta')
                if 'errors' in data: data.pop('errors')
                final_data = data

        standard_response = {
            'success': success,
            'data': final_data,
            'meta': meta,
            'errors': errors
        }

        return super(EnterpriseJSONRenderer, self).render(standard_response, accepted_media_type, renderer_context)
