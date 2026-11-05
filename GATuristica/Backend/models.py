from django.db import models

# Importar modelos de subdominios para que Django los detecte (Fase 16)
from .operativa_turistica import *
from .gestion_comercial import models as comercial_models
from .gestion_financiera import models as financiera_models
from .gestion_archivistica import models as archivistica_models
