from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.schemas.common import APIResponse
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/categories", tags=["Categories"])

@router.post("", response_model=APIResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=409, detail="Category name already exists")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return APIResponse(message="Category created", data=CategoryResponse.model_validate(cat))

@router.get("", response_model=List[CategoryResponse])
def list_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Category).offset(skip).limit(limit).all()

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    return cat

@router.delete("/{category_id}", response_model=APIResponse)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    cat = db.query(Category).filter(Category.id == category_id).first()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    if any(p.is_active for p in cat.products):
        raise HTTPException(status_code=400, detail="Cannot delete category containing active products")
    cat.is_active = False
    db.commit()
    return APIResponse(message="Category deleted (soft-delete)")
