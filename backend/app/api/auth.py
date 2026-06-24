from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.auth_service import register_user, login_user
from app.services.auth_schemas import UserCreate, UserLogin, TokenResponse, UserResponse, UserUpdate
from app.api.deps import get_current_user
from app.models.user import User
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(data: UserCreate, db: Session = Depends(get_db)):
    user = register_user(db, data)
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=TokenResponse)
def login(data: UserLogin, db: Session = Depends(get_db)):
    token, user = login_user(db, data)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(
    data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.full_name is not None:
        current_user.full_name = data.full_name.strip()
    if data.bio is not None:
        current_user.bio = data.bio.strip()
    if data.avatar_url is not None:
        current_user.avatar_url = data.avatar_url.strip()
    db.commit()
    db.refresh(current_user)
    return UserResponse.model_validate(current_user)
