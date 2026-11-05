# domain/services/funnel_service.py
 
from infrastructure.models import LandingPage, Embudo, Subcategoria, Tenant
from django.shortcuts import get_object_or_404
from django.utils.text import slugify

def get_public_funnel_by_slug(slug: str) -> Embudo:
    """
    Obtiene la estructura completa de un embudo publicado a través de su slug.
    Optimizado para la API pública, sin autenticación.
    """
    landing_page = get_object_or_404(LandingPage, slug=slug, estado='publicado')

    # Usamos prefetch_related para optimizar la consulta y traer todas las páginas y bloques
    # en un número reducido de queries a la base de datos.
    return Embudo.objects.prefetch_related('paginas__bloques').get(landing_page=landing_page)

def get_funnel_for_builder(tenant_id: int, funnel_id: int) -> Embudo:
    """
    Obtiene la estructura de un embudo para el constructor, verificando que
    pertenezca al tenant correcto.
    """
    # Aquí, asumimos que el embudo está directamente relacionado con el tenant
    # a través de la LandingPage y su jerarquía. Una forma más directa sería
    # añadir una FK de Embudo a Tenant. Por ahora, seguimos la jerarquía.
    try:
        embudo = Embudo.objects.select_related('landing_page__subcategoria__categoria__tenant').get(id=funnel_id)
        if embudo.landing_page.subcategoria.categoria.tenant.id != tenant_id:
            raise Embudo.DoesNotExist
        return embudo
    except Embudo.DoesNotExist:
        raise ValueError("Funnel not found in this tenant.")

# Aquí se añadirían más funciones de dominio como:
def create_full_funnel(tenant: Tenant, subcategoria_id: int, nombre_embudo: str) -> Embudo:
    """
    Crea la jerarquía completa de LandingPage y Embudo.
    """
    subcategoria = get_object_or_404(Subcategoria, id=subcategoria_id, categoria__tenant=tenant)

    # Crear un slug único para la LandingPage
    slug = slugify(nombre_embudo)
    unique_slug = slug
    counter = 1
    while LandingPage.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1

    landing_page = LandingPage.objects.create(subcategoria=subcategoria, slug=unique_slug)
    embudo = Embudo.objects.create(landing_page=landing_page, nombre=nombre_embudo)
    return embudo

def publish_funnel(tenant: Tenant, funnel_id: int) -> LandingPage:
    """
    Publica el embudo cambiando el estado de su LandingPage.
    """
    embudo = get_funnel_for_builder(tenant.id, funnel_id)
    landing_page = embudo.landing_page
    landing_page.estado = 'publicado'
    landing_page.save()
    return landing_page
 
