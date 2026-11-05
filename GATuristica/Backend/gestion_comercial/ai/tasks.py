# ai/tasks.py
from celery import shared_task
from infrastructure.models import AsyncTask
import time

@shared_task
def generate_video_task(async_task_id: int, prompt: str):
    """
    Tarea asíncrona de Celery para generar un video.
    """
    try:
        task = AsyncTask.objects.get(id=async_task_id)
        task.status = 'processing'
        task.save()

        # --- Simulación de la llamada a la IA de video ---
        print(f"Iniciando generación de video para el prompt: {prompt}")
        time.sleep(15) # Simula un proceso largo
        result_url = f"http://example.com/videos/{async_task_id}.mp4"
        print("Generación de video completada.")
        # --- Fin de la simulación ---

        task.status = 'completed'
        task.result_url = result_url
        task.save()

    except AsyncTask.DoesNotExist:
        print(f"Error: AsyncTask con id {async_task_id} no encontrado.")
    except Exception as e:
        print(f"Error en la tarea de generación de video: {e}")
        if 'task' in locals():
            task.status = 'failed'
            task.error_message = str(e)
            task.save()
