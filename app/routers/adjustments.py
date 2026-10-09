from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.adjustment import Adjustment
from app.schemas.adjustment import AdjustmentCreate, AdjustmentResponse
from app.schemas.common import APIResponse
from app.services.adjustment_service import create_adjustment, approve_adjustment
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/adjustments", tags=["Stock Adjustments"])

@router.post("", response_model=APIResponse, status_code=201)
def request_adjustments(
    data: AdjustmentCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    adj = create_adjustment(db, data, user.id)
    return APIResponse(message="Adjustment request recorded", data=AdjustmentResponse.model_validate(adj))

@router.get("", response_model=List[AdjustmentResponse])
def list_adjustments(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Adjustment).all()

@router.put("/{adjustment_id}/approve", response_model=APIResponse)
def approve_adjustments(
    adjustment_id: int,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    adj = approve_adjustment(db, adjustment_id, user.id)
    return APIResponse(message="Adjustment approved and stock corrected", data=AdjustmentResponse.model_validate(adj))
