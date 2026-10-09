from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserRegister, UserLogin, UserResponse, Token
from app.schemas.common import APIResponse
from app.services.auth_service import register_user, authenticate_user
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=APIResponse, status_code=201)
def register(data: UserRegister, db: Session = Depends(get_db)):
    user = register_user(db, data)
    return APIResponse(message="User registered successfully", data=UserResponse.model_validate(user))

@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):
    token = authenticate_user(db, data)
    return Token(access_token=token, token_type="bearer")

@router.get("/me", response_model=UserResponse)
def get_me(user = Depends(get_current_active_user)):
    return user
