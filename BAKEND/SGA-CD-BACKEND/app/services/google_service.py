import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleService:
    """
    A service to interact with various Google Workspace APIs.
    """

    def __init__(self, refresh_token: str):
        if not refresh_token:
            raise ValueError("A Google refresh token is required to use this service.")

        self.credentials = Credentials.from_authorized_user_info(
            info={
                "refresh_token": refresh_token,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        )
        logger.info("GoogleService initialized with credentials.")

    def _build_service(self, service_name: str, version: str):
        """Helper to build an authenticated Google API service client."""
        logger.info(f"Building Google API service: {service_name} v{version}")
        return build(service_name, version, credentials=self.credentials)

    def send_gmail(self, to: str, subject: str, body: str) -> dict:
        """Sends an email using the user's Gmail account."""
        try:
            import base64
            from email.message import EmailMessage

            gmail_service = self._build_service('gmail', 'v1')

            message = EmailMessage()
            message.set_content(body)
            message['To'] = to
            message['Subject'] = subject

            # Encode the message in base64url format.
            encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

            create_message = {'raw': encoded_message}
            send_request = gmail_service.users().messages().send(userId='me', body=create_message)
            sent_message = send_request.execute()

            logger.info(f"Email sent successfully to {to}. Message ID: {sent_message.get('id')}")
            return sent_message
        except Exception as e:
            logger.error(f"Failed to send email via Gmail: {e}")
            raise

    def upload_to_drive(self, file_path: str, file_name: str, mime_type: str = 'application/octet-stream') -> dict:
        """Uploads a file to the user's Google Drive."""
        try:
            from googleapiclient.http import MediaFileUpload
            import os

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File to upload not found at: {file_path}")

            drive_service = self._build_service('drive', 'v3')

            file_metadata = {'name': file_name}
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)

            file = drive_service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()

            file_id = file.get('id')
            file_link = file.get('webViewLink')
            logger.info(f"File '{file_name}' uploaded successfully to Drive. ID: {file_id}")
            return {'id': file_id, 'link': file_link}
        except Exception as e:
            logger.error(f"Failed to upload file to Drive: {e}")
            raise

    def export_to_sheets(self, sheet_name: str, data: list) -> dict:
        """
        Creates a new Google Sheet and populates it with the given data.
        'data' should be a list of lists, e.g., [['Header1', 'Header2'], ['Value1', 'Value2']].
        """
        try:
            sheets_service = self._build_service('sheets', 'v4')

            # 1. Create a new spreadsheet
            spreadsheet = {
                'properties': {
                    'title': sheet_name
                }
            }
            spreadsheet = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId,spreadsheetUrl').execute()
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            spreadsheet_url = spreadsheet.get('spreadsheetUrl')
            logger.info(f"Spreadsheet created successfully. ID: {spreadsheet_id}")

            # 2. Write data to the first sheet
            body = {
                'values': data
            }
            result = sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='A1',  # Start at the beginning of the first sheet
                valueInputOption='RAW',
                body=body
            ).execute()

            logger.info(f"{result.get('updatedCells')} cells updated in spreadsheet.")
            return {'id': spreadsheet_id, 'link': spreadsheet_url}
        except Exception as e:
            logger.error(f"Failed to export data to Sheets: {e}")
            raise

    def create_calendar_event(self, summary: str, start_datetime: str, end_datetime: str, attendees: list = None) -> dict:
        """
        Creates an event on the user's primary Google Calendar.
        Datetimes should be in ISO 8601 format, e.g., '2023-12-25T10:00:00-05:00'.
        """
        try:
            calendar_service = self._build_service('calendar', 'v3')

            event = {
                'summary': summary,
                'start': {
                    'dateTime': start_datetime,
                    'timeZone': 'America/Bogota', # Or fetch user's timezone
                },
                'end': {
                    'dateTime': end_datetime,
                    'timeZone': 'America/Bogota',
                },
            }
            if attendees:
                event['attendees'] = [{'email': email} for email in attendees]

            created_event = calendar_service.events().insert(calendarId='primary', body=event).execute()

            event_id = created_event.get('id')
            event_link = created_event.get('htmlLink')
            logger.info(f"Event created successfully. ID: {event_id}")
            return {'id': event_id, 'link': event_link}
        except Exception as e:
            logger.error(f"Failed to create calendar event: {e}")
            raise
