from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth import UserRegister, UserLogin
from app.auth.password import get_password_hash, verify_password
from app.auth.jwt import create_access_token
from app.utils.enums import UserRole

def register_user(db: Session, data: UserRegister) -> User:
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    if data.assigned_warehouse_id:
        from app.models.warehouse import Warehouse
        warehouse = db.query(Warehouse).filter(Warehouse.id == data.assigned_warehouse_id).first()
        if not warehouse:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Warehouse with ID {data.assigned_warehouse_id} not found"
            )
    user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        role=data.role,
        assigned_warehouse_id=data.assigned_warehouse_id
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, data: UserLogin) -> str:
    user = db.query(User).filter(User.email == data.email).first()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User account is inactive")
    token = create_access_token(data={"sub": user.email, "role": user.role.value, "id": user.id})
    return token
