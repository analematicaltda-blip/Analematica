import os
from pathlib import Path
import httplib2
import requests
import tempfile
from typing import Dict, Any

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials

# --- Constants ---
CLIENT_SECRETS_FILE = os.environ.get('YOUTUBE_CLIENT_SECRETS_FILE', str(Path(__file__).resolve().parents[2] / 'client_secrets.json'))
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

class VideoDistributionService:
    """
    A service to distribute a video to social media platforms.
    """
    def __init__(self, settings: Dict[str, str]):
        self.settings = settings

    def _get_youtube_service(self):
        """
        Builds the YouTube service object using stored credentials.
        """
        refresh_token = self.settings.get("youtube_refresh_token")

        if not os.path.exists(CLIENT_SECRETS_FILE):
            raise ValueError("client_secrets.json not found.")

        if not refresh_token:
            raise ValueError("YouTube refresh token not found. Please perform the one-time OAuth authorization.")

        credentials = OAuth2Credentials(
            access_token=None, # Will be refreshed automatically
            client_id=self.settings.get("google_client_id"),
            client_secret=self.settings.get("google_client_secret"),
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            token_expiry=None,
            user_agent="SGA-CD-Backend"
        )

        http = credentials.authorize(httplib2.Http())
        service = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=http)
        return service

    def publish_video_to_youtube(self, video_path: str, title: str, description: str) -> Dict[str, Any]:
        """Legacy uploads lack publication review and durable recovery."""
        raise RuntimeError("LEGACY_PUBLISH_DISABLED_USE_POOL08_CALENDAR")

    def publish_video(self, platform: str, video_url: str, title: str, description: str) -> Dict[str, Any]:
        """Legacy uploads lack publication review and durable recovery."""
        raise RuntimeError("LEGACY_PUBLISH_DISABLED_USE_POOL08_CALENDAR")

    def _publish_video_to_meta(self, video_path: str, title: str, description: str) -> Dict[str, Any]:
        """Legacy uploads lack publication review and durable recovery."""
        raise RuntimeError("LEGACY_PUBLISH_DISABLED_USE_POOL08_CALENDAR")


def get_distribution_service(db_session) -> VideoDistributionService:
    from app import crud
    import json
    try:
        with open(CLIENT_SECRETS_FILE, 'r') as f:
            secrets = json.load(f).get("installed", {})
    except FileNotFoundError:
        secrets = {}

    # Fetch all necessary tokens and keys from the database
    youtube_refresh_token_obj = crud.settings.get_setting(db_session, "youtube_refresh_token")
    meta_page_id_obj = crud.settings.get_setting(db_session, "meta_page_id")
    meta_token_obj = crud.settings.get_setting(db_session, "meta_page_access_token")

    settings = {
        # YouTube Credentials
        "youtube_refresh_token": youtube_refresh_token_obj.value if youtube_refresh_token_obj else None,
        "google_client_id": secrets.get("client_id"),
        "google_client_secret": secrets.get("client_secret"),
        # Meta Credentials
        "meta_page_id": meta_page_id_obj.value if meta_page_id_obj else None,
        "meta_page_access_token": meta_token_obj.value if meta_token_obj else None,
    }
    return VideoDistributionService(settings=settings)
