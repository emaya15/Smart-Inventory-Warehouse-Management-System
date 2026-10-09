from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
import datetime
from app.models.sales_order import SalesOrder
from app.models.return_model import Return, ReturnItem
from app.schemas.return_schema import ReturnCreate
from app.utils.enums import SOStatus, ReturnStatus, ReturnCondition, MovementType
from app.utils.helpers import generate_document_number
from app.services.inventory_service import change_inventory_stock
from app.services.audit_service import log_audit
from app.services.notification_service import send_email_background

def create_return(db: Session, so_id: int, data: ReturnCreate, user_id: int) -> Return:
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).first()
    if not so or so.status != SOStatus.DELIVERED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Return allowed only for Delivered orders")

    if so.delivered_at and (datetime.datetime.utcnow() - so.delivered_at).days > 7:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Return window (7 days) has expired")

    so_item_map = {item.product_id: item for item in so.items}
    ret_num = generate_document_number("RET", db, Return, "return_number")
    ret = Return(return_number=ret_num, sales_order_id=so.id, status=ReturnStatus.REQUESTED, created_by=user_id)
    db.add(ret)
    db.flush()

    refund_subtotal = 0.0
    for r_item in data.items:
        if r_item.product_id not in so_item_map:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product {r_item.product_id} not part of order")
        orig_item = so_item_map[r_item.product_id]
        if r_item.quantity > orig_item.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Return quantity exceeds ordered quantity")
        refund_subtotal += float(orig_item.unit_price) * r_item.quantity
        
        item_obj = ReturnItem(
            return_id=ret.id,
            product_id=r_item.product_id,
            quantity=r_item.quantity,
            condition_type=r_item.condition_type,
            reason=r_item.reason
        )
        db.add(item_obj)

    ret.refund_amount = round(refund_subtotal * 1.18, 2)
    log_audit(db, user_id, "REQUEST_RETURN", "Return", ret.id)
    db.commit()
    db.refresh(ret)
    return ret

def approve_return(db: Session, return_id: int, user_id: int, bg_tasks: BackgroundTasks) -> Return:
    ret = db.query(Return).filter(Return.id == return_id).with_for_update().first()
    if not ret or ret.status != ReturnStatus.REQUESTED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Return not in valid state for approval")

    so = ret.sales_order
    for r_item in ret.items:
        if r_item.condition_type == ReturnCondition.GOOD:
            change_inventory_stock(
                db=db,
                product_id=r_item.product_id,
                warehouse_id=so.warehouse_id,
                delta=r_item.quantity,
                movement_type=MovementType.CUSTOMER_RETURN,
                reference_id=ret.return_number,
                user_id=user_id
            )

    ret.status = ReturnStatus.APPROVED
    log_audit(db, user_id, "APPROVE", "Return", ret.id)
    db.commit()
    db.refresh(ret)

    bg_tasks.add_task(
        send_email_background,
        so.customer.email,
        f"Return Approved: {ret.return_number}",
        f"<p>Refund of ₹{ret.refund_amount} processed.</p>"
    )
    return ret
