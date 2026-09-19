from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.jwt import decode_token
from app.models.user import User

bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth"
)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token = credentials.credentials
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise credentials_error
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
        parsed_user_id = UUID(user_id)
    except Exception as exc:
        raise credentials_error from exc

    user = db.get(User, parsed_user_id)
    if not user:
        raise credentials_error
    if user.is_blocked:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is blocked")
    return user
