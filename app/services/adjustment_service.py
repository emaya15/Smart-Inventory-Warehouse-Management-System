from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.adjustment import Adjustment
from app.schemas.adjustment import AdjustmentCreate
from app.utils.enums import AdjustmentStatus, MovementType
from app.utils.helpers import generate_document_number
from app.services.inventory_service import change_inventory_stock
from app.services.audit_service import log_audit

def create_adjustment(db: Session, data: AdjustmentCreate, user_id: int) -> Adjustment:
    adj_num = generate_document_number("ADJ", db, Adjustment, "adjustment_number")
    adj = Adjustment(
        adjustment_number=adj_num,
        warehouse_id=data.warehouse_id,
        product_id=data.product_id,
        quantity_delta=data.quantity_delta,
        reason=data.reason,
        status=AdjustmentStatus.PENDING,
        created_by=user_id
    )
    db.add(adj)
    log_audit(db, user_id, "CREATE", "Adjustment", adj_num)
    db.commit()
    db.refresh(adj)
    return adj

def approve_adjustment(db: Session, adjustment_id: int, user_id: int) -> Adjustment:
    adj = db.query(Adjustment).filter(Adjustment.id == adjustment_id).with_for_update().first()
    if not adj or adj.status != AdjustmentStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Adjustment is not in Pending status")

    change_inventory_stock(
        db=db,
        product_id=adj.product_id,
        warehouse_id=adj.warehouse_id,
        delta=adj.quantity_delta,
        movement_type=MovementType.ADJUSTMENT,
        reference_id=adj.adjustment_number,
        user_id=user_id
    )
    adj.status = AdjustmentStatus.APPROVED
    adj.approved_by = user_id
    log_audit(db, user_id, "APPROVE", "Adjustment", adj.id)
    db.commit()
    db.refresh(adj)
    return adj
