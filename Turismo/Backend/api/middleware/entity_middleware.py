from ..models import Entity

class EntityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        host = request.get_host().split(':')[0]
        subdomain = host.split('.')[0]

        try:
            # Asumiendo que el dominio principal es localhost o un dominio de producción.
            # Esto necesita ser más robusto en un entorno de producción real.
            if subdomain != 'localhost' and subdomain != 'www':
                entity = Entity.objects.get(slug=subdomain)
                request.entity = entity
            else:
                request.entity = None
        except Entity.DoesNotExist:
            request.entity = None

        response = self.get_response(request)
        return response