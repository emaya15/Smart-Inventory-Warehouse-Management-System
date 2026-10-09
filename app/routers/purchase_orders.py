from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.purchase_order import PurchaseOrder
from app.schemas.purchase_order import POCreate, POResponse, POItemReceive
from app.schemas.common import APIResponse
from app.services.purchase_order_service import create_purchase_order, approve_purchase_order, receive_purchase_order
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/purchase-orders", tags=["Purchase Orders"])

@router.post("", response_model=APIResponse, status_code=201)
def create_purchase_orders(
    data: POCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    po = create_purchase_order(db, data, user.id)
    return APIResponse(message="Purchase order created", data=POResponse.model_validate(po))

@router.get("", response_model=List[POResponse])
def list_purchase_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(PurchaseOrder).offset(skip).limit(limit).all()

@router.put("/{po_id}/approve", response_model=APIResponse)
def approve_purchase_orders(
    po_id: int,
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    po = approve_purchase_order(db, po_id, user.id, bg_tasks)
    return APIResponse(message="PO approved successfully", data=POResponse.model_validate(po))

@router.post("/{po_id}/receive", response_model=APIResponse)
def receive_purchase_orders(
    po_id: int,
    items: List[POItemReceive],
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    po = receive_purchase_order(db, po_id, items, user.id)
    return APIResponse(message="Goods received into inventory", data=POResponse.model_validate(po))
