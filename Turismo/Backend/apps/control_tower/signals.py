from django.db.models.signals import post_save
from django.dispatch import receiver
from .domain.alert import Alert
from .infrastructure.alert_dispatcher import AlertDispatcher

@receiver(post_save, sender=Alert)
def on_alert_created(sender, instance, created, **kwargs):
    if created:
        AlertDispatcher.dispatch(instance.id)
