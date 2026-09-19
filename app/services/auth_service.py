from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.core.security import hash_password, verify_password
from app.firebase.firebase import verify_google_id_token
from app.models.enums import UserRole
from app.models.user import User
from app.schemas.auth import GoogleLoginRequest, LoginRequest, ProviderRegisterRequest, TokenResponse
from app.schemas.user import UserRegister
from app.services.helpers import ensure_email_unique, ensure_phone_unique, validate_category_ids


def register_user(db: Session, payload: UserRegister) -> User:
    ensure_email_unique(db, payload.email)
    ensure_phone_unique(db, payload.phone)
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=UserRole.CUSTOMER,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def register_provider(db: Session, payload: ProviderRegisterRequest) -> TokenResponse:
    ensure_email_unique(db, payload.email)
    ensure_phone_unique(db, payload.phone)
    provider_category_ids = validate_category_ids(db, payload.category_ids)
    user = User(
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        hashed_password=hash_password(payload.password),
        role=UserRole.PROVIDER,
        organization_name=payload.organization_name,
        responsible_person=payload.responsible_person,
        provider_category_ids=provider_category_ids,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _tokens_for_user(user)


def login_user(db: Session, payload: LoginRequest) -> TokenResponse:
    identifier = payload.identifier or payload.email or payload.phone
    user = db.scalar(
        select(User).where(
            or_(
                User.email == identifier,
                User.phone == identifier,
                User.email == payload.email,
                User.phone == payload.phone,
            )
        )
    )
    if not user or not user.hashed_password or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is blocked")

    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id), user.role.value),
        role=user.role,
    )


def _tokens_for_user(user: User) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id), user.role.value),
        role=user.role,
    )


def login_with_google(db: Session, payload: GoogleLoginRequest) -> TokenResponse:
    decoded_token = verify_google_id_token(payload.id_token)
    firebase_uid = decoded_token.get("uid")
    email = decoded_token.get("email")
    email_verified = decoded_token.get("email_verified")

    if not firebase_uid or not email or not email_verified:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Google account email is not verified")

    user = db.scalar(select(User).where(User.firebase_uid == firebase_uid))
    if not user:
        user = db.scalar(select(User).where(User.email == email))

    if user:
        if user.is_blocked:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is blocked")
        user.firebase_uid = firebase_uid
        user.full_name = user.full_name or decoded_token.get("name") or email.split("@", 1)[0]
        if not user.avatar_url and decoded_token.get("picture"):
            user.avatar_url = decoded_token["picture"]
    else:
        user = User(
            full_name=decoded_token.get("name") or email.split("@", 1)[0],
            email=email,
            hashed_password=None,
            firebase_uid=firebase_uid,
            avatar_url=decoded_token.get("picture"),
            role=UserRole.CUSTOMER,
        )
        db.add(user)

    db.commit()
    db.refresh(user)
    return _tokens_for_user(user)


def refresh_user_token(db: Session, refresh_token: str) -> TokenResponse:
    try:
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise ValueError
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token") from exc

    user = db.get(User, UUID(payload["sub"]))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is blocked")

    return TokenResponse(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id), user.role.value),
        role=user.role,
    )


def change_user_password(db: Session, user: User, current_password: str, new_password: str) -> None:
    if not user.hashed_password or not verify_password(current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")

    user.hashed_password = hash_password(new_password)
    db.commit()
