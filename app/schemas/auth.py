from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, model_validator

from app.models.enums import UserRole


class LoginRequest(BaseModel):
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    identifier: str | None = Field(default=None, min_length=3, max_length=150)
    password: str = Field(min_length=6, max_length=128)

    @model_validator(mode="after")
    def validate_identifier(self):
        if not self.email and not self.phone and not self.identifier:
            raise ValueError("email, phone or identifier is required")
        return self


class ProviderRegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=7, max_length=32)
    password: str = Field(min_length=6, max_length=128)
    organization_name: str = Field(min_length=2, max_length=150)
    responsible_person: str = Field(min_length=2, max_length=100)
    category_ids: list[UUID] = Field(min_length=1)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    id_token: str = Field(min_length=10)


class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=6, max_length=128)
    new_password: str = Field(min_length=6, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    role: UserRole
