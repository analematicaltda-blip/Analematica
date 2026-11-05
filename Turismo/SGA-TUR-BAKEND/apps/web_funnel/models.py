from django.db import models
from django.utils.translation import gettext_lazy as _

class MediaAsset(models.Model):
    """
    Representa un archivo multimedia (imagen, video, etc.) que puede ser utilizado
    en varios bloques de contenido.
    """
    nombre = models.CharField(_("Nombre"), max_length=200, help_text=_("Un nombre descriptivo para el archivo."))
    archivo = models.FileField(_("Archivo"), upload_to='web_funnel_media/')
    tipo = models.CharField(_("Tipo de archivo"), max_length=50, blank=True, help_text=_("Ej: 'image/jpeg', 'video/mp4'"))
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        verbose_name = _("Activo Multimedia")
        verbose_name_plural = _("Activos Multimedia")

class WebPage(models.Model):
    """
    Representa una página web estática dentro del funnel.
    """
    title = models.CharField(_("Título"), max_length=200, help_text=_("El título principal de la página."))
    slug = models.SlugField(_("Slug"), max_length=200, unique=True, help_text=_("La URL amigable de la página (ej. 'pagina-de-ventas')."))
    is_published = models.BooleanField(_("Está Publicada"), default=False, help_text=_("Indica si la página es visible públicamente."))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Página Web")
        verbose_name_plural = _("Páginas Web")
        ordering = ['title']

class Section(models.Model):
    """
    Representa una sección dentro de una WebPage.
    """
    web_page = models.ForeignKey(WebPage, related_name='sections', on_delete=models.CASCADE, verbose_name=_("Página Web"))
    title = models.CharField(_("Título de la Sección"), max_length=200)
    order = models.PositiveIntegerField(_("Orden"), default=0, help_text=_("El orden de la sección dentro de la página."))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.web_page.title})"

    class Meta:
        verbose_name = _("Sección")
        verbose_name_plural = _("Secciones")
        ordering = ['web_page', 'order']

class ContentBlock(models.Model):
    """
    Representa un bloque de contenido dentro de una Sección.
    """
    section = models.ForeignKey(Section, related_name='content_blocks', on_delete=models.CASCADE, verbose_name=_("Sección"))
    CONTENT_TYPE_CHOICES = [
        ('text', _('Texto')),
        ('image', _('Imagen')),
        ('video', _('Video')),
        ('button', _('Botón')),
    ]
    content_type = models.CharField(
        _("Tipo de Contenido"),
        max_length=10,
        choices=CONTENT_TYPE_CHOICES,
        default='text'
    )
    content = models.TextField(_("Contenido"), blank=True, help_text=_("Contenido de texto, URL de imagen/video, o texto del botón."))
    link = models.URLField(_("Enlace"), blank=True, null=True, help_text=_("URL para imágenes, videos o botones."))
    order = models.PositiveIntegerField(_("Orden"), default=0, help_text=_("El orden del bloque dentro de la sección."))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_content_type_display()} - {self.section.title}"

    class Meta:
        verbose_name = _("Bloque de Contenido")
        verbose_name_plural = _("Bloques de Contenido")
        ordering = ['section', 'order']
