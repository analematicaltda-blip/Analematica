# domain/services/video_generation_service.py
from infrastructure.models import User, AsyncTask
from ai.tasks import generate_video_task

def start_video_generation(user: User, prompt: str) -> AsyncTask:
    """
    Crea un registro de tarea asíncrona y lanza la tarea de Celery.
    """
    task = AsyncTask.objects.create(
        tenant=user.tenant,
        user=user,
        task_type='video_generation',
        status='pending'
    )

    # Lanzar la tarea de Celery en segundo plano
    generate_video_task.delay(async_task_id=task.id, prompt=prompt)

    return task
