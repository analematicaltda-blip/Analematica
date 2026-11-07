import os
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage

# --- Configuration ---
CLIENT_SECRETS_FILE = "client_secrets.json"
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
CREDENTIALS_FILE = "youtube_credentials.json" # This file will store the refresh token

def run_oauth_flow():
    """
    Performs the one-time OAuth 2.0 consent flow to get a refresh token.
    """
    if not os.path.exists(CLIENT_SECRETS_FILE):
        print(f"ERROR: The client secrets file '{CLIENT_SECRETS_FILE}' was not found.")
        print("Please download it from your Google Cloud Console and place it in the same directory as this script.")
        return

    # Create a flow object from the client secrets file.
    flow = flow_from_clientsecrets(
        CLIENT_SECRETS_FILE,
        scope=YOUTUBE_UPLOAD_SCOPE,
        redirect_uri='http://localhost:8080/' # Must match one of the authorized redirect URIs in your GCP project
    )

    # Get the authorization URL
    auth_uri = flow.step1_get_authorize_url()

    print("\n" + "="*80)
    print(" === Google OAuth 2.0 Refresh Token Generator === ")
    print("="*80)
    print("\n1. Please open the following URL in your web browser:")
    print(f"\n   {auth_uri}\n")
    print("2. Log in to the Google account you want to use for YouTube uploads.")
    print("3. Grant the application permission to upload videos on your behalf.")
    print("4. After granting permission, you will be redirected to a 'localhost' URL.")
    print("   Your browser will likely show a 'This site can’t be reached' error. This is NORMAL.")
    print("5. Copy the ENTIRE URL from your browser's address bar. It will look something like:")
    print("   http://localhost:8080/?code=4/0A...&scope=https://www.googleapis.com/auth/youtube.upload")
    print("\n6. Paste the full URL here and press Enter:")

    redirect_response_url = input("\nPaste the full redirect URL here: ").strip()

    try:
        # Exchange the authorization code for a refresh token
        credentials = flow.step2_exchange(redirect_response_url)

        # The credentials object now contains the refresh token.
        # We can save it to a file for later use or just print it.
        storage = Storage(CREDENTIALS_FILE)
        storage.put(credentials)

        print("\n" + "="*80)
        print("✅ SUCCESS!")
        print(f"Credentials (including the refresh token) have been saved to '{CREDENTIALS_FILE}'")
        print("\nYour REFRESH TOKEN is:")
        print(f"   {credentials.refresh_token}")
        print("\nCopy this refresh token and save it in the application's settings page for the 'admin_general'.")
        print("="*80)

    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        print("Please try the process again.")

if __name__ == "__main__":
    run_oauth_flow()
