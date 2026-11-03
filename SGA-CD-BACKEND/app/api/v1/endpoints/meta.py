import secrets
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from urllib.parse import urlencode

from app.api import deps
from app.core.config import settings

router = APIRouter()

META_BASE_URL = "https://www.facebook.com/v19.0/dialog/oauth"
SCOPES = [
    "pages_show_list",
    "pages_read_engagement",
    "pages_manage_posts",
    "read_insights",
    "instagram_basic",
    "instagram_manage_insights",
    "instagram_content_publish"
]

@router.get("/meta/login")
def meta_login():
    """
    Redirects the user to Meta's OAuth consent screen.
    """
    # TODO: Implement proper CSRF protection using session-based state.
    # For now, we use a simple state, but it's not validated on callback.
    state = secrets.token_urlsafe(16)

    redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/meta/callback"

    params = {
        "client_id": settings.META_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": ",".join(SCOPES),
        "response_type": "code",
        "state": state,
    }
    login_url = f"{META_BASE_URL}?{urlencode(params)}"

    return RedirectResponse(url=login_url)


import requests
from fastapi.responses import HTMLResponse
from app import crud

# ... (other code)

@router.get("/meta/callback")
def meta_callback(code: str, state: str, db: Session = Depends(deps.get_db)):
    """
    Handles the callback from Meta's OAuth flow.
    Exchanges the code for a long-lived page access token and stores it.
    """
    # TODO: Validate the 'state' parameter against one stored in the user's session.

    # 1. Exchange code for a short-lived user access token
    token_url = "https://graph.facebook.com/v19.0/oauth/access_token"
    redirect_uri = f"{settings.SERVER_HOST}{settings.API_V1_STR}/auth/meta/callback"
    token_params = {
        "client_id": settings.META_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "client_secret": settings.META_CLIENT_SECRET,
        "code": code,
    }
    r = requests.get(token_url, params=token_params)
    token_data = r.json()
    if "error" in token_data:
        raise HTTPException(status_code=400, detail=f"Error getting token: {token_data['error']['message']}")

    short_lived_token = token_data["access_token"]

    # 2. Exchange the short-lived token for a long-lived one
    long_lived_params = {
        "grant_type": "fb_exchange_token",
        "client_id": settings.META_CLIENT_ID,
        "client_secret": settings.META_CLIENT_SECRET,
        "fb_exchange_token": short_lived_token,
    }
    r = requests.get(token_url, params=long_lived_params)
    long_lived_data = r.json()
    if "error" in long_lived_data:
        raise HTTPException(status_code=400, detail=f"Error getting long-lived token: {long_lived_data['error']['message']}")

    long_lived_user_token = long_lived_data["access_token"]

    # 3. Get the user's pages and find one with an Instagram account
    pages_url = f"https://graph.facebook.com/me/accounts"
    pages_params = {
        "fields": "name,access_token,instagram_business_account{name,username}",
        "access_token": long_lived_user_token,
    }
    r = requests.get(pages_url, params=pages_params)
    pages_data = r.json()

    if "error" in pages_data:
        raise HTTPException(status_code=400, detail=f"Error fetching pages: {pages_data['error']['message']}")

    target_page = None
    for page in pages_data.get("data", []):
        if "instagram_business_account" in page:
            target_page = page
            break

    if not target_page:
        raise HTTPException(status_code=404, detail="No Facebook Page with a connected Instagram Business Account was found.")

    page_id = target_page["id"]
    page_name = target_page["name"]
    page_access_token = target_page["access_token"]
    ig_username = target_page["instagram_business_account"]["username"]

    # 4. Save the long-lived page access token and page ID to the database
    # This uses a placeholder function that we will implement in the next step.
    crud.settings.update_setting(db, key="meta_page_access_token", value=page_access_token)
    crud.settings.update_setting(db, key="meta_page_id", value=page_id)
    crud.settings.update_setting(db, key="meta_page_name", value=page_name)
    crud.settings.update_setting(db, key="meta_ig_username", value=ig_username)

    # 5. Return a user-friendly HTML response
    html_content = """
    <html>
        <head>
            <title>Authentication Successful</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding-top: 50px; }
                .container { max-width: 600px; margin: auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
                .success { color: #28a745; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1 class="success">¡Autenticación Exitosa!</h1>
                <p>La cuenta de Instagram <strong>""" + ig_username + """</strong> (asociada a la página de Facebook <strong>""" + page_name + """</strong>) se ha conectado correctamente.</p>
                <p>Ya puede cerrar esta ventana.</p>
            </div>
            <script>
                // Optional: attempt to close the window
                setTimeout(() => { window.close(); }, 3000);
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.get("/meta/status")
def meta_status(db: Session = Depends(deps.get_db)):
    """
    Checks if a Meta account is connected by looking for stored credentials.
    """
    page_name_obj = crud.settings.get_setting(db, "meta_page_name")
    ig_username_obj = crud.settings.get_setting(db, "meta_ig_username")

    if page_name_obj and page_name_obj.value and ig_username_obj and ig_username_obj.value:
        return {
            "connected": True,
            "page_name": page_name_obj.value,
            "ig_username": ig_username_obj.value,
        }

    return {"connected": False}
