import os
import requests
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MetaUploader:
    """
    A dedicated class to handle resumable video uploads to the Facebook Graph API.
    Implements chunking and a simple retry mechanism.
    """
    BASE_URL = "https://graph-video.facebook.com/v19.0"
    CHUNK_SIZE = 4 * 1024 * 1024  # 4 MB
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 5

    def __init__(self, page_id: str, page_access_token: str):
        if not page_id or not page_access_token:
            raise ValueError("Page ID and Page Access Token are required.")
        self.page_id = page_id
        self.page_access_token = page_access_token
        self.api_url = f"{self.BASE_URL}/{self.page_id}/videos"

    def _make_request(self, method, url, **kwargs):
        """Disabled legacy protocol: no placeholder receipts or unsafe retries."""
        raise RuntimeError("LEGACY_PUBLISH_DISABLED_USE_POOL08_CALENDAR")

    def _start_upload_session(self, file_size: int) -> str:
        """Starts a resumable upload session and returns the upload session ID."""
        logging.info(f"Starting Meta video upload session for file size: {file_size} bytes")
        params = {
            "upload_phase": "start",
            "access_token": self.page_access_token,
            "file_size": file_size,
        }
        response = self._make_request("POST", self.api_url, params=params)
        upload_session_id = response.get("upload_session_id")
        if not upload_session_id:
            raise ValueError("Failed to get upload_session_id from Meta.")
        logging.info(f"Upload session started successfully. Session ID: {upload_session_id}")
        return upload_session_id

    def _transfer_chunk(self, upload_session_id: str, chunk: bytes, start_offset: int) -> int:
        """Uploads a single chunk of the video."""
        logging.info(f"Uploading chunk, offset: {start_offset}, size: {len(chunk)} bytes")
        params = {
            "upload_phase": "transfer",
            "access_token": self.page_access_token,
            "upload_session_id": upload_session_id,
            "start_offset": start_offset,
        }
        headers = {'Content-Type': 'application/octet-stream'}
        response = self._make_request("POST", self.api_url, params=params, data=chunk, headers=headers)
        # The response should contain the new start_offset, but we track it ourselves.
        return len(chunk)

    def _finish_upload_session(self, upload_session_id: str, title: str, description: str) -> dict:
        """Disabled legacy protocol: no placeholder receipts or unsafe retries."""
        raise RuntimeError("LEGACY_PUBLISH_DISABLED_USE_POOL08_CALENDAR")

    def upload_video(self, video_path: str, title: str, description: str) -> dict:
        """Disabled legacy protocol: no placeholder receipts or unsafe retries."""
        raise RuntimeError("LEGACY_PUBLISH_DISABLED_USE_POOL08_CALENDAR")
