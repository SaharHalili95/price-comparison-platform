import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.core.rate_limiter import limiter
from app.core.security import decode_token
from app.models.user import User
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    MessageResponse,
)
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
@limiter.limit("5/minute")
async def register(
    request: Request,
    body: UserRegisterRequest,
    db: Session = Depends(get_db),
):
    """Register a new user account."""
    try:
        user = AuthService.register_user(
            db=db,
            email=body.email,
            username=body.username,
            password=body.password,
            full_name=body.full_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    AuthService.log_event(db, "register", user_id=user.id, request=request)
    return user


@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
async def login(
    request: Request,
    body: UserLoginRequest,
    db: Session = Depends(get_db),
):
    """Authenticate and receive JWT tokens."""
    user = AuthService.authenticate_user(db, body.email, body.password)

    if not user:
        AuthService.log_event(
            db, "login_failed", request=request, success=False, details=body.email
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token, refresh_token, expires_in = AuthService.create_session(db, user, request)
    AuthService.log_event(db, "login", user_id=user.id, request=request)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=expires_in,
    )


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute")
async def refresh_token(
    request: Request,
    body: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Rotate refresh token and get new access token."""
    result = AuthService.refresh_session(db, body.refresh_token, request)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    access_token, new_refresh_token, expires_in = result

    try:
        payload = decode_token(access_token)
        user_id = int(payload.get("sub"))
        AuthService.log_event(db, "token_refresh", user_id=user_id, request=request)
    except Exception:
        pass

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=expires_in,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request: Request,
    body: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logout: blacklist access token and revoke refresh token."""
    auth_header = request.headers.get("authorization", "")
    access_token_str = auth_header.replace("Bearer ", "")

    try:
        access_payload = decode_token(access_token_str)
        access_jti = access_payload.get("jti")
        access_exp = datetime.utcfromtimestamp(access_payload.get("exp"))
    except Exception:
        access_jti = "unknown"
        access_exp = datetime.utcnow()

    AuthService.logout(db, access_jti, access_exp, body.refresh_token, current_user.id)
    AuthService.log_event(db, "logout", user_id=current_user.id, request=request)

    return MessageResponse(message="Successfully logged out")


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Get the current authenticated user's profile."""
    return current_user
