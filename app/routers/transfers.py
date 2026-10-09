from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.transfer import Transfer
from app.schemas.transfer import TransferCreate, TransferResponse
from app.schemas.common import APIResponse
from app.services.transfer_service import create_transfer, dispatch_transfer, receive_transfer
from app.auth.roles import require_roles
from app.utils.enums import UserRole
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/transfers", tags=["Stock Transfers"])

@router.post("", response_model=APIResponse, status_code=201)
def new_transfer(
    data: TransferCreate,
    db: Session = Depends(get_db),
    user = Depends(require_roles([UserRole.ADMIN, UserRole.INVENTORY_MANAGER]))
):
    tr = create_transfer(db, data, user.id)
    return APIResponse(message="Transfer created", data=TransferResponse.model_validate(tr))

@router.get("", response_model=List[TransferResponse])
def list_transfers(db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    return db.query(Transfer).all()

@router.put("/{transfer_id}/dispatch", response_model=APIResponse)
def dispatch_transfers(transfer_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    tr = dispatch_transfer(db, transfer_id, user.id)
    return APIResponse(message="Transfer dispatched", data=TransferResponse.model_validate(tr))

@router.put("/{transfer_id}/receive", response_model=APIResponse)
def receive_transfers(transfer_id: int, db: Session = Depends(get_db), user = Depends(get_current_active_user)):
    tr = receive_transfer(db, transfer_id, user.id)
    return APIResponse(message="Transfer received at destination", data=TransferResponse.model_validate(tr))
