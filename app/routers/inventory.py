from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.inventory import Inventory
from app.schemas.inventory import InventoryResponse
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.get("", response_model=List[InventoryResponse])
def get_inventory(
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    q = db.query(Inventory)
    if product_id:
        q = q.filter(Inventory.product_id == product_id)
    if warehouse_id:
        q = q.filter(Inventory.warehouse_id == warehouse_id)
    return q.all()

@router.get("/{product_id}/{warehouse_id}", response_model=InventoryResponse)
def get_specific_inventory(
    product_id: int,
    warehouse_id: int,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    inv = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.warehouse_id == warehouse_id
    ).first()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return inv
