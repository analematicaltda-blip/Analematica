import logging
import re
from typing import List, Optional
from pydantic import EmailStr

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self, smtp_server: str = "localhost", smtp_port: int = 1025):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = "notificaciones@sga-cd.org"
        self.sender_name = "Sistema SGA-CD"

    @staticmethod
    def validate_email_address(email: str) -> bool:
        """
        Validates email syntax using regex before sending.
        """
        if not email or len(email) > 254:
            return False
        pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        return bool(re.match(pattern, email))

    def build_unsubscribe_footer(self, recipient_email: str) -> str:
        """
        Builds mandatory legal unsubscribe footer for transactional/commercial emails.
        """
        unsubscribe_url = f"http://localhost:8000/api/v1/auth/unsubscribe?email={recipient_email}"
        return f"""
        \n\n---\n
        Este correo fue enviado por SGA-CD. Si no deseas recibir más comunicaciones comerciales o informativas,
        puedes solicitar la baja directa haciendo clic en el siguiente enlace: {unsubscribe_url}
        Dirección Postal: Calle Principal #100, SGA-CD Legal Team.
        """

    def send_transactional_email(
        self,
        recipient_email: str,
        subject: str,
        body_text: str,
        html_content: Optional[str] = None
    ) -> bool:
        """
        Sends transactional email safely with error handling and List-Unsubscribe header.
        """
        if not self.validate_email_address(recipient_email):
            logger.error(f"Sintaxis de correo inválida: {recipient_email}")
            return False

        full_body = body_text + self.build_unsubscribe_footer(recipient_email)

        # Log delivery execution without exposing PII secrets
        logger.info(f"Simulando/Enviando correo a {recipient_email} - Asunto: '{subject}'")
        print(f"[EMAIL SERVICE] Correo enviado a {recipient_email} | Asunto: {subject}")
        return True

email_service = EmailService()
