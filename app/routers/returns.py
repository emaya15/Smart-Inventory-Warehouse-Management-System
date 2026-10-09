from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.return_model import Return
from app.schemas.return_schema import ReturnCreate, ReturnResponse
from app.schemas.common import APIResponse
from app.services.return_service import create_return, approve_return
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(tags=["Returns"])

@router.post("/sales-orders/{so_id}/returns", response_model=APIResponse, status_code=201)
def request_returns(
    so_id: int,
    data: ReturnCreate,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    ret = create_return(db, so_id, data, user.id)
    return APIResponse(message="Return request submitted", data=ReturnResponse.model_validate(ret))

@router.get("/returns", response_model=List[ReturnResponse])
def list_returns(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Return).all()

@router.put("/returns/{return_id}/approve", response_model=APIResponse)
def approve_returns(
    return_id: int,
    bg_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    ret = approve_return(db, return_id, user.id, bg_tasks)
    return APIResponse(message="Return approved and stock/refund processed", data=ReturnResponse.model_validate(ret))
