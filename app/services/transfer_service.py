from sqlalchemy.orm import Session
from fastapi import HTTPException, status
import datetime
from app.models.transfer import Transfer, TransferItem
from app.models.warehouse import Warehouse
from app.models.inventory import Inventory
from app.schemas.transfer import TransferCreate
from app.utils.enums import TransferStatus, MovementType
from app.utils.helpers import generate_document_number
from app.services.inventory_service import change_inventory_stock
from app.services.audit_service import log_audit

def create_transfer(db: Session, data: TransferCreate, user_id: int) -> Transfer:
    if data.source_warehouse_id == data.destination_warehouse_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source and destination cannot be the same")
    tr_num = generate_document_number("TR", db, Transfer, "transfer_number")
    tr = Transfer(
        transfer_number=tr_num,
        source_warehouse_id=data.source_warehouse_id,
        destination_warehouse_id=data.destination_warehouse_id,
        status=TransferStatus.PENDING,
        created_by=user_id
    )
    db.add(tr)
    db.flush()

    for it in data.items:
        tr_item = TransferItem(transfer_id=tr.id, product_id=it.product_id, quantity=it.quantity)
        db.add(tr_item)

    log_audit(db, user_id, "CREATE", "Transfer", tr.id)
    db.commit()
    db.refresh(tr)
    return tr

def dispatch_transfer(db: Session, transfer_id: int, user_id: int) -> Transfer:
    tr = db.query(Transfer).filter(Transfer.id == transfer_id).with_for_update().first()
    if not tr or tr.status != TransferStatus.PENDING:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer not in Pending state")

    for item in tr.items:
        change_inventory_stock(
            db=db,
            product_id=item.product_id,
            warehouse_id=tr.source_warehouse_id,
            delta=-item.quantity,
            movement_type=MovementType.TRANSFER_OUT,
            reference_id=tr.transfer_number,
            user_id=user_id
        )

    tr.status = TransferStatus.IN_TRANSIT
    tr.dispatched_at = datetime.datetime.utcnow()
    log_audit(db, user_id, "DISPATCH", "Transfer", tr.id)
    db.commit()
    db.refresh(tr)
    return tr

def receive_transfer(db: Session, transfer_id: int, user_id: int) -> Transfer:
    tr = db.query(Transfer).filter(Transfer.id == transfer_id).with_for_update().first()
    if not tr or tr.status != TransferStatus.IN_TRANSIT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer not in In-Transit state")

    for item in tr.items:
        change_inventory_stock(
            db=db,
            product_id=item.product_id,
            warehouse_id=tr.destination_warehouse_id,
            delta=item.quantity,
            movement_type=MovementType.TRANSFER_IN,
            reference_id=tr.transfer_number,
            user_id=user_id
        )
        item.received_quantity = item.quantity

    tr.status = TransferStatus.RECEIVED
    tr.received_at = datetime.datetime.utcnow()
    log_audit(db, user_id, "RECEIVE", "Transfer", tr.id)
    db.commit()
    db.refresh(tr)
    return tr
