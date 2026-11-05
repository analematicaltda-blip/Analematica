 
# backend/puerto_gaitan_turismo/celery.py
import os
from celery import Celery

# Establecer el módulo de configuración de Django para el proceso de Celery.
 
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'puerto_gaitan_turismo.settings')

app = Celery('puerto_gaitan_turismo')

 
# Usar una cadena aquí significa que el worker no necesita serializar
# el objeto de configuración. El namespace='CELERY' significa que
# todas las claves de configuración de Celery deben tener un prefijo `CELERY_`.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Si las variables de entorno no están definidas, usa Redis local por defecto.
app.conf.broker_url = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
app.conf.result_backend = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

# Cargar automáticamente los módulos de tareas de todas las aplicaciones registradas.
 
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
