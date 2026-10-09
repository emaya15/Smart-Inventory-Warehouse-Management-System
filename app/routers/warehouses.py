from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseUpdate, WarehouseResponse
from app.schemas.inventory import InventoryResponse
from app.schemas.common import APIResponse
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/warehouses", tags=["Warehouses"])

@router.post("", response_model=APIResponse, status_code=201)
def create_warehouse(
    data: WarehouseCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN]))
):
    if db.query(Warehouse).filter(Warehouse.warehouse_code == data.warehouse_code).first():
        raise HTTPException(status_code=409, detail="Warehouse code already exists")
    wh = Warehouse(**data.model_dump())
    db.add(wh)
    db.commit()
    db.refresh(wh)
    return APIResponse(message="Warehouse created", data=WarehouseResponse.model_validate(wh))

@router.get("", response_model=List[WarehouseResponse])
def list_warehouses(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Warehouse).all()

@router.get("/{warehouse_id}/inventory", response_model=List[InventoryResponse])
def get_warehouse_inventory(warehouse_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    return wh.inventories
