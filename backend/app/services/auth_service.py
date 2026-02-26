import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Session as DBSession
from fastapi import Request

from app.models.user import User
from app.models.session import Session
from app.models.token_blacklist import TokenBlacklist
from app.models.audit_log import AuditLog
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token, _utcnow
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:

    @staticmethod
    def register_user(
        db: DBSession,
        email: str,
        username: str,
        password: str,
        full_name: Optional[str] = None,
    ) -> User:
        if db.query(User).filter(User.email == email.lower()).first():
            raise ValueError("Email already registered")
        if db.query(User).filter(User.username == username).first():
            raise ValueError("Username already taken")

        user = User(
            email=email.lower(),
            username=username,
            hashed_password=hash_password(password),
            full_name=full_name,
            role="user",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(
        db: DBSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        user = db.query(User).filter(User.email == email.lower()).first()

        if not user:
            return None

        # Check account lockout
        if user.locked_until and user.locked_until > _utcnow():
            return None

        # Reset lockout if expired
        if user.locked_until and user.locked_until <= _utcnow():
            user.locked_until = None
            user.failed_login_attempts = 0

        if not verify_password(password, user.hashed_password):
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                user.locked_until = _utcnow() + timedelta(
                    minutes=settings.LOCKOUT_DURATION_MINUTES
                )
            db.commit()
            return None

        # Successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = _utcnow()
        db.commit()
        return user

    @staticmethod
    def create_session(
        db: DBSession,
        user: User,
        request: Optional[Request] = None,
    ) -> tuple:
        """Create tokens and session record. Returns (access_token, refresh_token, expires_in)."""
        access_token, access_jti, access_expires = create_access_token(user.id, user.role)
        refresh_token, refresh_jti, refresh_expires = create_refresh_token(user.id)

        device_info = None
        ip_address = None
        if request:
            ip_address = request.client.host if request.client else None
            device_info = json.dumps({
                "user_agent": request.headers.get("user-agent", ""),
                "ip": ip_address,
            })

        session = Session(
            user_id=user.id,
            refresh_token_jti=refresh_jti,
            device_info=device_info,
            ip_address=ip_address,
            expires_at=refresh_expires,
        )
        db.add(session)
        db.commit()

        expires_in = int((access_expires - _utcnow()).total_seconds())
        return access_token, refresh_token, expires_in

    @staticmethod
    def refresh_session(
        db: DBSession,
        refresh_token_str: str,
        request: Optional[Request] = None,
    ) -> Optional[tuple]:
        """Validate refresh token, rotate it, return new tokens."""
        try:
            payload = decode_token(refresh_token_str)
        except Exception:
            return None

        if payload.get("type") != "refresh":
            return None

        jti = payload.get("jti")
        user_id = int(payload.get("sub"))

        # Check blacklist
        if db.query(TokenBlacklist).filter(TokenBlacklist.jti == jti).first():
            return None

        # Find session
        session = db.query(Session).filter(
            Session.refresh_token_jti == jti,
            Session.is_revoked == False,
        ).first()

        if not session:
            return None

        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if not user:
            return None

        # Revoke old refresh token (rotation)
        session.is_revoked = True
        db.add(TokenBlacklist(
            jti=jti,
            token_type="refresh",
            user_id=user_id,
            expires_at=session.expires_at,
        ))

        # Create new session
        access_token, new_refresh_token, expires_in = AuthService.create_session(db, user, request)
        return access_token, new_refresh_token, expires_in

    @staticmethod
    def logout(
        db: DBSession,
        access_token_jti: str,
        access_expires: datetime,
        refresh_token_str: Optional[str],
        user_id: int,
    ):
        """Blacklist access token and revoke refresh session."""
        db.add(TokenBlacklist(
            jti=access_token_jti,
            token_type="access",
            user_id=user_id,
            expires_at=access_expires,
        ))

        if refresh_token_str:
            try:
                payload = decode_token(refresh_token_str)
                refresh_jti = payload.get("jti")
                session = db.query(Session).filter(
                    Session.refresh_token_jti == refresh_jti
                ).first()
                if session:
                    session.is_revoked = True
                db.add(TokenBlacklist(
                    jti=refresh_jti,
                    token_type="refresh",
                    user_id=user_id,
                    expires_at=session.expires_at if session else _utcnow(),
                ))
            except Exception:
                pass

        db.commit()

    @staticmethod
    def log_event(
        db: DBSession,
        event_type: str,
        user_id: Optional[int] = None,
        request: Optional[Request] = None,
        success: bool = True,
        details: Optional[str] = None,
    ):
        entry = AuditLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=request.client.host if request and request.client else None,
            user_agent=request.headers.get("user-agent") if request else None,
            details=details,
            success=success,
        )
        db.add(entry)
        db.commit()
