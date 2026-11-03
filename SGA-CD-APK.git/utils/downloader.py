import requests
import os
from threading import Thread

def download_file(url: str, local_path: str, progress_callback: callable, completion_callback: callable):
    """
    Downloads a file from a URL to a local path in a separate thread.

    Args:
        url (str): The URL of the file to download.
        local_path (str): The local path (including filename) to save the file.
        progress_callback (callable): A function to call with progress updates.
                                      It receives (current_bytes, total_bytes).
        completion_callback (callable): A function to call when the download is complete or fails.
                                        It receives (success: bool, error_message: str | None).
    """

    def _download_target():
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))

                with open(local_path, 'wb') as f:
                    downloaded_size = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        progress_callback(downloaded_size, total_size)

            completion_callback(True, None)

        except requests.exceptions.RequestException as e:
            completion_callback(False, f"Error de red: {e}")
        except Exception as e:
            completion_callback(False, f"Error inesperado: {e}")

    thread = Thread(target=_download_target)
    thread.start()
