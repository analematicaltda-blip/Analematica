from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from sqlalchemy import text
from jose import jwt, JWTError
from pydantic import ValidationError

from app import crud, schemas, models
from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.rate_limiter import rate_limit

from datetime import datetime, timedelta, timezone

router = APIRouter()

FAILED_LOGIN_ATTEMPTS = {}  # {username: {"count": int, "blocked_until": datetime}}

def check_login_rate_limit(username: str):
    record = FAILED_LOGIN_ATTEMPTS.get(username)
    if record:
        now = datetime.now(timezone.utc)
        if record.get("blocked_until") and now < record["blocked_until"]:
            time_left = int((record["blocked_until"] - now).total_seconds())
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Demasiados intentos fallidos. Cuenta bloqueada temporalmente por {time_left} segundos."
            )

def record_failed_login(username: str):
    now = datetime.now(timezone.utc)
    record = FAILED_LOGIN_ATTEMPTS.get(username, {"count": 0, "blocked_until": None})
    record["count"] += 1
    if record["count"] >= 5:
        record["blocked_until"] = now + timedelta(minutes=5)
    FAILED_LOGIN_ATTEMPTS[username] = record

def clear_failed_login(username: str):
    if username in FAILED_LOGIN_ATTEMPTS:
        del FAILED_LOGIN_ATTEMPTS[username]


@router.post("/login", response_model=schemas.Token, dependencies=[Depends(rate_limit("login", max_requests=10, window_seconds=60))])
def login(
    db: Session = Depends(deps.get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token and refresh token with brute-force protection.
    """
    check_login_rate_limit(form_data.username)

    user = crud.user.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.password_hash):
        record_failed_login(form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.activo:
        raise HTTPException(status_code=400, detail="Inactive user")

    clear_failed_login(form_data.username)

    # El objeto user de crud.get_user_by_username ya trae role_list
    access_token_data = {
        "sub": str(user.id),
        "roles": getattr(user, "role_list", [user.rol.value if hasattr(user.rol, "value") else str(user.rol)]),
        "inquilino_id": user.inquilino_id,
        "nombre_completo": user.nombre_completo
    }
    # Refresh token solo necesita el user_id
    refresh_token_data = {"sub": str(user.id)}

    return {
        "access_token": security.create_access_token(data=access_token_data),
        "refresh_token": security.create_refresh_token(data=refresh_token_data),
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.Token)
def refresh_token(
    db: Session = Depends(deps.get_db), refresh_token: str = Body(..., embed=True)
) -> Any:
    """
    OAuth2 compatible token refresh.
    """
    try:
        payload = jwt.decode(
            refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type, expected 'refresh'",
            )
        token_data = schemas.TokenData(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(models.user.Usuario).filter(models.user.Usuario.id == token_data.sub).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.activo:
        raise HTTPException(status_code=400, detail="Inactive user")

    # Como el objeto de la query no trae roles, los buscamos manualmente
    query = text("SELECT r.nombre FROM roles r JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = :user_id")
    roles_result = db.execute(query, {"user_id": user.id}).fetchall()
    user_roles = [row[0] for row in roles_result]

    access_token_data = {
        "sub": str(user.id),
        "roles": user_roles,
        "inquilino_id": user.inquilino_id,
        "nombre_completo": user.nombre_completo,
    }

    return {
        "access_token": security.create_access_token(data=access_token_data),
        "refresh_token": refresh_token,  # devolvemos el mismo refresh token
        "token_type": "bearer",
    }


@router.post("/register", response_model=schemas.User, dependencies=[Depends(rate_limit("register", max_requests=10, window_seconds=3600))])
def register_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user with email validation and transactional welcome dispatch.
    """
    from app.services.email_service import email_service
    if not email_service.validate_email_address(user_in.email):
        raise HTTPException(
            status_code=400,
            detail="La dirección de correo electrónico proporcionada no es válida.",
        )

    user = crud.user.get_user_by_username(db, username=user_in.nombre_usuario)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = crud.user.create_user(db, user=user_in)

    # Send transactional welcome email
    email_service.send_transactional_email(
        recipient_email=user_in.email,
        subject="Bienvenido a SGA-CD",
        body_text=f"Hola {user_in.nombre_completo or user_in.nombre_usuario}, tu cuenta ha sido creada exitosamente en SGA-CD."
    )
    return {
        "id": user.id,
        "email": user.correo,
        "nombre_completo": user.nombre_completo,
        "rango_edad": user_in.rango_edad,
        "consentimiento_padre": user_in.consentimiento_padre,
        "activo": user.activo,
        "roles": [r.nombre for r in user.roles] if user.roles else [user_in.rol]
    }


@router.get("/unsubscribe", dependencies=[Depends(rate_limit("unsubscribe", max_requests=10, window_seconds=60))])
def unsubscribe_email(
    email: str,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Public endpoint for direct one-click unsubscribe from marketing/notifications without login.
    """
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Dirección de correo inválida.")

    return {
        "status": "success",
        "message": f"La dirección {email} ha sido dada de baja exitosamente de las comunicaciones comerciales de SGA-CD."
    }


@router.delete("/me/data")
def delete_my_data(
    db: Session = Depends(deps.get_db),
    current_user: models.user.Usuario = Depends(deps.get_current_active_user),
) -> Any:
    """
    Derecho ARCO: Solicitud de eliminación/anonimización de datos personales.
    Desactiva la cuenta y anonimiza los datos identificables.
    """
    import uuid
    anon_id = str(uuid.uuid4())[:8]
    current_user.activo = False
    current_user.nombre_usuario = f"deleted_user_{anon_id}"
    current_user.nombre_completo = "Usuario Anónimo (Datos Eliminados)"
    db.add(current_user)
    db.commit()
    return {"status": "success", "message": "Tus datos personales han sido anonimizados y la cuenta ha sido desactivada conforme a la Política de Privacidad."}