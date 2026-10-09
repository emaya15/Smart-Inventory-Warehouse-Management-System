from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierResponse
from app.schemas.common import APIResponse
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.utils.validators import validate_phone, validate_gst
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])

@router.post("", response_model=APIResponse, status_code=201)
def create_suppliers(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    validate_phone(data.phone)
    validate_gst(data.gst_number)
    if db.query(Supplier).filter(Supplier.supplier_code == data.supplier_code).first():
        raise HTTPException(status_code=409, detail="Supplier code exists")
    sup = Supplier(**data.model_dump())
    db.add(sup)
    db.commit()
    db.refresh(sup)
    return APIResponse(message="Supplier created", data=SupplierResponse.model_validate(sup))

@router.get("", response_model=List[SupplierResponse])
def list_suppliers(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Supplier).filter(Supplier.is_active == True).all()
