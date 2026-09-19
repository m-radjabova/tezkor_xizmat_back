from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.auth import ChangePasswordRequest, GoogleLoginRequest, LoginRequest, ProviderRegisterRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth_service import change_user_password, login_user, login_with_google, refresh_user_token, register_provider

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/customer/google", response_model=TokenResponse)
def customer_google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    return login_with_google(db, payload)


@router.post("/provider/register", response_model=TokenResponse)
def provider_register(payload: ProviderRegisterRequest, db: Session = Depends(get_db)):
    return register_provider(db, payload)


@router.post("/provider/login", response_model=TokenResponse)
def provider_login(payload: LoginRequest, db: Session = Depends(get_db)):
    return login_user(db, payload)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    return refresh_user_token(db, payload.refresh_token)


@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    change_user_password(db, current_user, payload.current_password, payload.new_password)
    return {"message": "Password changed successfully"}
