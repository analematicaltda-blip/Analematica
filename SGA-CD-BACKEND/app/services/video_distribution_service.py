import os
import httplib2
import requests
import tempfile
from typing import Dict, Any

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from oauth2client.client import OAuth2Credentials

# --- Constants ---
CLIENT_SECRETS_FILE = "SGA-CD-FASTAPI-BACKEND/client_secrets.json"
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
        """
        Uploads a video from a local file path to YouTube.
        """
        try:
            youtube = self._get_youtube_service()
            body = {
                "snippet": { "title": title, "description": description, "tags": [], "categoryId": "22" },
                "status": { "privacyStatus": "private" }
            }
            insert_request = youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
            )
            response = insert_request.execute()
            video_id = response.get("id")
            if not video_id:
                raise ValueError("YouTube API did not return a video ID.")
            return {
                "status": "success",
                "platform": "youtube",
                "post_url": f"https://www.youtube.com/watch?v={video_id}"
            }
        except Exception as e:
            print(f"An error occurred during YouTube upload: {e}")
            raise

    def publish_video(self, platform: str, video_url: str, title: str, description: str) -> Dict[str, Any]:
        """
        Downloads a video from a URL and publishes it to the specified platform.
        """
        if platform.lower() == "youtube":
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                try:
                    print(f"Downloading video from {video_url} to {tmp_file.name}...")
                    response = requests.get(video_url, stream=True)
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    print("Download complete.")

                    # Get the full path of the temporary file
                    video_path = tmp_file.name

                    return self.publish_video_to_youtube(video_path, title, description)
                finally:
                    # Ensure the temporary file is deleted
                    os.unlink(video_path)
                    print(f"Deleted temporary file: {video_path}")
        elif platform.lower() in ["facebook", "instagram"]:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
                try:
                    print(f"Downloading video from {video_url} for Meta upload...")
                    response = requests.get(video_url, stream=True)
                    response.raise_for_status()
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_file.write(chunk)
                    print("Download complete.")
                    video_path = tmp_file.name
                    return self._publish_video_to_meta(video_path, title, description)
                finally:
                    os.unlink(video_path)
                    print(f"Deleted temporary file: {video_path}")
        else:
            raise NotImplementedError(f"Platform '{platform}' is not supported for video distribution.")

    def _publish_video_to_meta(self, video_path: str, title: str, description: str) -> Dict[str, Any]:
        """
        Publishes a video to the connected Meta (Facebook/Instagram) page.
        """
        from .meta_uploader import MetaUploader

        page_id = self.settings.get("meta_page_id")
        page_access_token = self.settings.get("meta_page_access_token")

        if not page_id or not page_access_token:
            raise ValueError("Meta Page ID or Page Access Token not configured.")

        uploader = MetaUploader(page_id=page_id, page_access_token=page_access_token)
        return uploader.upload_video(video_path=video_path, title=title, description=description)


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
