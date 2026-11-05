import logging
from django.core.mail import send_mail
from django.conf import settings
from ..domain.alert import Alert

logger = logging.getLogger(__name__)

class AlertDispatcher:
    """
    Infrastructure service to dispatch alerts across multiple channels.
    """

    @staticmethod
    def dispatch(alert_id):
        """
        Main entry point for alert dispatching.
        """
        alert = Alert.objects.get(id=alert_id)

        # 1. Log locally
        logger.info(f"Dispatching Alert {alert.id}: {alert.title}")

        # 2. Channel: Dashboard (Already handled by persistence)

        # 3. Channel: Email (For CRITICAL alerts)
        if alert.severity in [Alert.Severity.CRITICAL, Alert.Severity.BLOCKING]:
            AlertDispatcher._send_email_notification(alert)

        # 4. Channel: Slack/Webhooks (Placeholder)
        AlertDispatcher._trigger_webhooks(alert)

    @staticmethod
    def _send_email_notification(alert):
        subject = f"[SARITA CONTROL TOWER] {alert.severity}: {alert.title}"
        message = (
            f"An alert has been triggered in the Control Tower.\n\n"
            f"Severity: {alert.severity}\n"
            f"Description: {alert.description}\n"
            f"Scope: {alert.entity_scope}\n"
            f"Tenant: {alert.tenant_id}\n"
        )

        # In a real environment, we'd fetch recipient lists from roles
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [admin[1] for admin in settings.ADMINS],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")

    @staticmethod
    def _trigger_webhooks(alert):
        # Implementation for outbound webhooks to third-party monitoring
        pass
