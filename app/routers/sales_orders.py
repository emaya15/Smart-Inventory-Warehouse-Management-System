from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.sales_order import SalesOrder
from app.schemas.sales_order import SOCreate, SODispatch, SOResponse
from app.schemas.common import APIResponse
from app.services.sales_order_service import (
    create_sales_order, confirm_sales_order, pick_sales_order,
    pack_sales_order, dispatch_sales_order, deliver_sales_order, cancel_sales_order
)
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/sales-orders", tags=["Sales Orders"])

@router.post("", response_model=APIResponse, status_code=201)
def create_sales_orders(
    data: SOCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    so = create_sales_order(db, data, user.id)
    return APIResponse(message="Sales order created", data=SOResponse.model_validate(so))

@router.get("", response_model=List[SOResponse])
def list_sales_orders(skip: int = 0, limit: int = 50, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(SalesOrder).offset(skip).limit(limit).all()

@router.put("/{so_id}/confirm", response_model=APIResponse)
def confirm_sales_orders(
    so_id: int,
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    so = confirm_sales_order(db, so_id, user.id, bg_tasks)
    return APIResponse(message="Sales order confirmed and stock reserved", data=SOResponse.model_validate(so))

@router.put("/{so_id}/pick", response_model=APIResponse)
def pick_sales_orders(so_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    so = pick_sales_order(db, so_id, user.id)
    return APIResponse(message="Sales order picked", data=SOResponse.model_validate(so))

@router.put("/{so_id}/pack", response_model=APIResponse)
def pack_sales_orders(so_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    so = pack_sales_order(db, so_id, user.id)
    return APIResponse(message="Sales order packed", data=SOResponse.model_validate(so))

@router.put("/{so_id}/dispatch", response_model=APIResponse)
def dispatch_sales_orders(
    so_id: int,
    data: SODispatch,
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    so = dispatch_sales_order(db, so_id, data, user.id, bg_tasks)
    return APIResponse(message="Sales order dispatched (FEFO applied)", data=SOResponse.model_validate(so))

@router.put("/{so_id}/deliver", response_model=APIResponse)
def deliver_sales_orders(so_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    so = deliver_sales_order(db, so_id, user.id)
    return APIResponse(message="Sales order delivered", data=SOResponse.model_validate(so))

@router.put("/{so_id}/cancel", response_model=APIResponse)
def cancel_sales_orders(so_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    so = cancel_sales_order(db, so_id, user.id)
    return APIResponse(message="Sales order cancelled and reserved stock released", data=SOResponse.model_validate(so))
