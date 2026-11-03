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
        """Wrapper for requests with retry logic."""
        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.request(method, url, **kwargs)
                response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
                return response.json()
            except requests.exceptions.RequestException as e:
                logging.warning(f"Request failed (attempt {attempt + 1}/{self.MAX_RETRIES}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(self.RETRY_DELAY_SECONDS * (2 ** attempt)) # Exponential backoff
                else:
                    logging.error("All retry attempts failed.")
                    raise

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
        """Finishes the upload session and publishes the video."""
        logging.info(f"Finishing Meta video upload session ID: {upload_session_id}")
        params = {
            "upload_phase": "finish",
            "access_token": self.page_access_token,
            "upload_session_id": upload_session_id,
            "title": title,
            "description": description,
        }
        response = self._make_request("POST", self.api_url, params=params)
        if not response.get("success"):
             raise ValueError(f"Failed to finalize video upload: {response}")
        logging.info("Video upload finalized successfully.")
        # We need to get the video ID to build the URL. This requires another call.
        # This is a simplification; a robust solution would query the video post's status.
        return {"id": "post_id_placeholder"} # The finish call doesn't return the post ID directly.

    def upload_video(self, video_path: str, title: str, description: str) -> dict:
        """
        Orchestrates the entire video upload process with chunking and retries.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        file_size = os.path.getsize(video_path)
        logging.info(f"Starting upload for video: {video_path} ({file_size} bytes)")

        try:
            session_id = self._start_upload_session(file_size)

            with open(video_path, "rb") as f:
                offset = 0
                while True:
                    chunk = f.read(self.CHUNK_SIZE)
                    if not chunk:
                        break
                    self._transfer_chunk(session_id, chunk, offset)
                    offset += len(chunk)

            result = self._finish_upload_session(session_id, title, description)

            # The Graph API does not return the post URL directly on finish.
            # A common practice is to query the page's feed for the video post
            # or construct a URL based on the page ID and the video ID (if obtainable).
            # For this implementation, we return a placeholder.
            post_id = result.get("id")
            return {
                "status": "success",
                "platform": "facebook",
                "post_url": f"https://www.facebook.com/{self.page_id}/videos/{post_id}"
            }
        except Exception as e:
            logging.error(f"Failed to upload video to Meta: {e}")
            raise
