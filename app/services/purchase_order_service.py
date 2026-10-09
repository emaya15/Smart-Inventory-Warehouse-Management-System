from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
import datetime
from app.models.purchase_order import PurchaseOrder, PurchaseOrderItem
from app.models.supplier import Supplier
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.batch import Batch
from app.schemas.purchase_order import POCreate, POItemReceive
from app.utils.enums import POStatus, MovementType
from app.utils.helpers import generate_document_number
from app.services.inventory_service import change_inventory_stock, get_or_create_inventory
from app.services.audit_service import log_audit
from app.services.notification_service import send_email_background

def create_purchase_order(db: Session, data: POCreate, user_id: int) -> PurchaseOrder:
    supplier = db.query(Supplier).filter(Supplier.id == data.supplier_id, Supplier.is_active == True).first()
    if not supplier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier not found or inactive")
    wh = db.query(Warehouse).filter(Warehouse.id == data.warehouse_id, Warehouse.is_active == True).first()
    if not wh:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warehouse not found or inactive")
    
    exp_date = data.expected_delivery_date or (datetime.date.today() + datetime.timedelta(days=supplier.lead_time_days))
    po_num = generate_document_number("PO", db, PurchaseOrder, "po_number")

    po = PurchaseOrder(
        po_number=po_num,
        supplier_id=data.supplier_id,
        warehouse_id=data.warehouse_id,
        expected_delivery_date=exp_date,
        status=POStatus.DRAFT,
        created_by=user_id
    )
    db.add(po)
    db.flush()

    total = 0.0
    for item in data.items:
        prod = db.query(Product).filter(Product.id == item.product_id, Product.is_active == True).first()
        if not prod:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid product ID {item.product_id}")
        line_cost = item.quantity_ordered * item.unit_cost
        total += line_cost
        po_item = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=item.product_id,
            quantity_ordered=item.quantity_ordered,
            unit_cost=item.unit_cost
        )
        db.add(po_item)

    po.total_amount = total
    log_audit(db, user_id, "CREATE", "PurchaseOrder", po.id, None, {"po_number": po_num, "total": total})
    db.commit()
    db.refresh(po)
    return po

def approve_purchase_order(db: Session, po_id: int, user_id: int, bg_tasks: BackgroundTasks) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).with_for_update().first()
    if not po or po.status != POStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PO can only be approved if in Draft status")
    po.status = POStatus.APPROVED
    log_audit(db, user_id, "APPROVE", "PurchaseOrder", po.id)
    db.commit()
    db.refresh(po)

    bg_tasks.add_task(
        send_email_background,
        po.supplier.email,
        f"Purchase Order Approved: {po.po_number}",
        f"<p>Your purchase order <b>{po.po_number}</b> has been approved.</p>"
    )
    return po

def receive_purchase_order(db: Session, po_id: int, items_received: list[POItemReceive], user_id: int) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).with_for_update().first()
    if not po:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PO not found")
    if po.status not in [POStatus.APPROVED, POStatus.PARTIALLY_RECEIVED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="PO not in receivable status")

    item_map = {item.product_id: item for item in po.items}

    for rec in items_received:
        if rec.product_id not in item_map:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product {rec.product_id} is not part of this PO")
        po_item = item_map[rec.product_id]
        if po_item.quantity_received + rec.quantity_received > po_item.quantity_ordered:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Received quantity exceeds ordered quantity")

        prod = db.query(Product).filter(Product.id == rec.product_id).with_for_update().first()
        inv = get_or_create_inventory(db, rec.product_id, po.warehouse_id)
        
        # Weighted Average Cost Calculation
        old_stock = inv.quantity_on_hand
        old_cost = float(prod.cost_price)
        new_units = rec.quantity_received
        purchase_cost = float(po_item.unit_cost)
        if (old_stock + new_units) > 0:
            weighted_cost = ((old_stock * old_cost) + (new_units * purchase_cost)) / (old_stock + new_units)
            prod.cost_price = round(weighted_cost, 2)

        # Update Inventory & Stock Movement
        change_inventory_stock(
            db=db,
            product_id=rec.product_id,
            warehouse_id=po.warehouse_id,
            delta=rec.quantity_received,
            movement_type=MovementType.PURCHASE_RECEIPT,
            reference_id=po.po_number,
            user_id=user_id
        )

        po_item.quantity_received += rec.quantity_received

        # Batch & Expiry Registration
        batch_num = rec.batch_number or f"BATCH-{po.po_number}-{rec.product_id}"
        mfg = rec.manufacturing_date or datetime.date.today()
        exp = rec.expiry_date or (datetime.date.today() + datetime.timedelta(days=365))
        
        batch = db.query(Batch).filter(Batch.product_id == rec.product_id, Batch.batch_number == batch_num).first()
        if batch:
            batch.quantity += rec.quantity_received
        else:
            batch = Batch(
                batch_number=batch_num,
                product_id=rec.product_id,
                warehouse_id=po.warehouse_id,
                quantity=rec.quantity_received,
                manufacturing_date=mfg,
                expiry_date=exp,
                unit_cost=po_item.unit_cost
            )
            db.add(batch)

    # Determine status
    all_received = all(item.quantity_received >= item.quantity_ordered for item in po.items)
    po.status = POStatus.RECEIVED if all_received else POStatus.PARTIALLY_RECEIVED
    if po.status == POStatus.RECEIVED:
        po.received_at = datetime.datetime.utcnow()

    log_audit(db, user_id, "RECEIVE", "PurchaseOrder", po.id)
    db.commit()
    db.refresh(po)
    return po
