import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile
from fastapi.responses import RedirectResponse, HTMLResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow

from app.api import deps
from app.core.config import settings
from app.services.google_service import GoogleService
from app import crud

router = APIRouter()

# Scopes define the permissions we are asking for.
SCOPES = [
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.send",
]

def get_google_flow(state=None):
    """
    Helper to create a Google OAuth2 flow instance.
    """
    # The client_secrets.json file is not used directly. Instead, the config
    # is built dynamically from the application settings for better security.
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/google/callback"],
        }
    }
    return Flow.from_client_config(client_config, scopes=SCOPES, state=state)

@router.get("/google/login")
def google_login():
    """
    Generates the authorization URL and redirects the user.
    """
    flow = get_google_flow()
    flow.redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/google/callback"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true'
    )
    # TODO: Store the 'state' in the user's session to prevent CSRF.
    return RedirectResponse(authorization_url)


@router.get("/google/callback")
def google_callback(request: Request, db: Session = Depends(deps.get_db)):
    """
    Handles the callback from Google, exchanges the code for a refresh token,
    and stores it.
    """
    # TODO: Validate the 'state' parameter against the one stored in the user's session.
    state = request.query_params.get('state')

    flow = get_google_flow(state=state)
    flow.redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/google/callback"

    # Use the full URL from the request to fetch the token.
    authorization_response = str(request.url)
    try:
        flow.fetch_token(authorization_response=authorization_response)
    except Exception as e:
        logging.error(f"Error fetching Google token: {e}")
        raise HTTPException(status_code=400, detail=f"Error fetching token: {e}")

    credentials = flow.credentials
    if not credentials.refresh_token:
        # This can happen if the user has already granted consent and is not re-prompted.
        # The 'prompt=consent' in the login URL should prevent this, but as a fallback.
        raise HTTPException(
            status_code=400,
            detail="A refresh token was not obtained. Please ensure you are granting offline access and re-consent if necessary."
        )

    # Save the refresh token to the database
    crud.settings.update_setting(db, key="google_refresh_token", value=credentials.refresh_token)

    html_content = """
    <html>
        <head>
            <title>Authentication Successful</title>
            <style>body { font-family: sans-serif; text-align: center; padding-top: 50px; }</style>
        </head>
        <body>
            <h1>¡Autenticación con Google Exitosa!</h1>
            <p>La plataforma ahora tiene el permiso necesario para acceder a los servicios de Google en su nombre.</p>
            <p>Ya puede cerrar esta ventana.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/google/status")
def google_status(db: Session = Depends(deps.get_db)):
    """
    Checks if a Google account is connected by looking for a refresh token.
    """
    token = crud.settings.get_setting(db, "google_refresh_token")
    if token and token.value:
        return {"connected": True}
    return {"connected": False}

# --- Pydantic Models for API requests ---
class EmailRequest(BaseModel):
    to: str
    subject: str
    body: str

class SheetRequest(BaseModel):
    sheet_name: str
    data: list[list]

class EventRequest(BaseModel):
    summary: str
    start_datetime: str
    end_datetime: str
    attendees: list[str] | None = None

# --- Helper function to get the service ---
def get_google_service(db: Session = Depends(deps.get_db)) -> GoogleService:
    token = crud.settings.get_setting(db, "google_refresh_token")
    if not token or not token.value:
        raise HTTPException(status_code=403, detail="Google account not connected or refresh token not found.")
    return GoogleService(refresh_token=token.value)

# --- Service Endpoints ---

@router.post("/google/send_email")
def send_email_endpoint(
    request: EmailRequest,
    service: GoogleService = Depends(get_google_service)
):
    try:
        return service.send_gmail(to=request.to, subject=request.subject, body=request.body)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google/export_sheets")
def export_sheets_endpoint(
    request: SheetRequest,
    service: GoogleService = Depends(get_google_service)
):
    try:
        return service.export_to_sheets(sheet_name=request.sheet_name, data=request.data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google/create_event")
def create_event_endpoint(
    request: EventRequest,
    service: GoogleService = Depends(get_google_service)
):
    try:
        return service.create_calendar_event(
            summary=request.summary,
            start_datetime=request.start_datetime,
            end_datetime=request.end_datetime,
            attendees=request.attendees
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google/upload_drive")
async def upload_drive_endpoint(
    file: UploadFile,
    service: GoogleService = Depends(get_google_service)
):
    try:
        # Save the uploaded file temporarily to disk to get a file path
        with tempfile.NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        result = service.upload_to_drive(
            file_path=tmp_path,
            file_name=file.filename,
            mime_type=file.content_type
        )
        os.unlink(tmp_path) # Clean up the temporary file
        return result
    except Exception as e:
        # Make sure to clean up temp file on error as well
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise HTTPException(status_code=500, detail=str(e))
