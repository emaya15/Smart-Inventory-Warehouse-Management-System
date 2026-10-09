from sqlalchemy.orm import Session
from fastapi import HTTPException, status, BackgroundTasks
import datetime
from app.models.sales_order import SalesOrder, SalesOrderItem
from app.models.customer import Customer
from app.models.warehouse import Warehouse
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.batch import Batch
from app.models.user import User
from app.schemas.sales_order import SOCreate, SODispatch
from app.utils.enums import SOStatus, MovementType
from app.utils.enums import UserRole
from app.utils.helpers import generate_document_number
from app.services.inventory_service import change_inventory_stock
from app.services.audit_service import log_audit
from app.services.notification_service import send_email_background

def create_sales_order(db: Session, data: SOCreate, user_id: int) -> SalesOrder:
    customer = db.query(Customer).filter(Customer.id == data.customer_id, Customer.is_active == True).first()
    if not customer:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Customer not found or inactive")
    wh = db.query(Warehouse).filter(Warehouse.id == data.warehouse_id, Warehouse.is_active == True).first()
    if not wh:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warehouse not found or inactive")

    so_num = generate_document_number("SO", db, SalesOrder, "so_number")
    so = SalesOrder(
        so_number=so_num,
        customer_id=data.customer_id,
        warehouse_id=data.warehouse_id,
        status=SOStatus.DRAFT,
        created_by=user_id
    )
    db.add(so)
    db.flush()

    subtotal = 0.0
    for it in data.items:
        prod = db.query(Product).filter(Product.id == it.product_id, Product.is_active == True).first()
        if not prod:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product {it.product_id} inactive or non-existent")
        price = float(prod.selling_price)
        line_total = price * it.quantity
        subtotal += line_total
        so_item = SalesOrderItem(
            sales_order_id=so.id,
            product_id=it.product_id,
            quantity=it.quantity,
            unit_price=price,
            line_total=line_total
        )
        db.add(so_item)

    tax = subtotal * 0.18
    grand_total = subtotal + tax
    
    # Check Customer Credit Limit
    if float(customer.credit_limit) > 0 and grand_total > float(customer.credit_limit):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order grand total exceeds customer credit limit")

    so.subtotal = subtotal
    so.tax_amount = tax
    so.grand_total = grand_total

    log_audit(db, user_id, "CREATE", "SalesOrder", so.id, None, {"so_number": so_num, "total": grand_total})
    db.commit()
    db.refresh(so)
    return so

def confirm_sales_order(db: Session, so_id: int, user_id: int, bg_tasks: BackgroundTasks) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).with_for_update().first()
    if not so or so.status != SOStatus.DRAFT:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Draft sales orders can be confirmed")

    for item in so.items:
        inv = db.query(Inventory).filter(
            Inventory.product_id == item.product_id,
            Inventory.warehouse_id == so.warehouse_id
        ).with_for_update().first()
        
        if not inv or (inv.quantity_on_hand - inv.quantity_reserved) < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient available stock for product ID {item.product_id}"
            )
        inv.quantity_reserved += item.quantity

    so.status = SOStatus.CONFIRMED
    log_audit(db, user_id, "CONFIRM", "SalesOrder", so.id)
    db.commit()
    db.refresh(so)

    bg_tasks.add_task(
        send_email_background,
        so.customer.email,
        f"Order Confirmed: {so.so_number}",
        f"<p>Your order <b>{so.so_number}</b> is confirmed. Total: ₹{so.grand_total}</p>"
    )
    return so

def pick_sales_order(db: Session, so_id: int, user_id: int) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).with_for_update().first()
    if not so or so.status != SOStatus.CONFIRMED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only pick Confirmed orders")
    so.status = SOStatus.PICKED
    log_audit(db, user_id, "PICK", "SalesOrder", so.id)
    db.commit()
    db.refresh(so)
    return so

def pack_sales_order(db: Session, so_id: int, user_id: int) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).with_for_update().first()
    if not so or so.status != SOStatus.PICKED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only pack PickED orders")
    so.status = SOStatus.PACKED
    log_audit(db, user_id, "PACK", "SalesOrder", so.id)
    db.commit()
    db.refresh(so)
    return so


def dispatch_sales_order(
    db: Session,
    so_id: int,
    data: SODispatch,
    user_id: int,
    bg_tasks: BackgroundTasks
) -> SalesOrder:

    so = (
        db.query(SalesOrder)
        .filter(SalesOrder.id == so_id)
        .with_for_update()
        .first()
    )

    if not so or so.status != SOStatus.PACKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only dispatch Packed orders"
        )

    existing_order = db.query(SalesOrder).filter(
        SalesOrder.tracking_number == data.tracking_number,
        SalesOrder.id != so_id
    ).first()

    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tracking number must be unique"
        )

    today = datetime.date.today()

    for item in so.items:

        # Find available, non-expired batches using FEFO
        batches = (
            db.query(Batch)
            .filter(
                Batch.product_id == item.product_id,
                Batch.warehouse_id == so.warehouse_id,
                Batch.quantity > 0,
                Batch.expiry_date >= today
            )
            .order_by(Batch.expiry_date.asc())
            .with_for_update()
            .all()
        )

        total_batch_qty = sum(batch.quantity for batch in batches)

        if total_batch_qty < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Insufficient non-expired batch stock "
                    f"for product {item.product_id}"
                )
            )

        # Deduct quantity from batches
        needed = item.quantity

        for batch in batches:
            if needed <= 0:
                break

            take = min(batch.quantity, needed)
            batch.quantity -= take
            needed -= take

        # Find inventory
        inv = (
            db.query(Inventory)
            .filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == so.warehouse_id
            )
            .with_for_update()
            .first()
        )

        if not inv:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Inventory not found for product {item.product_id}"
            )

        if inv.quantity_reserved < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient reserved stock for product {item.product_id}"
            )

        # Release the reservation.
        # Do not manually reduce quantity_on_hand here:
        # change_inventory_stock() handles the stock reduction.
        inv.quantity_reserved -= item.quantity

        change_inventory_stock(
            db=db,
            product_id=item.product_id,
            warehouse_id=so.warehouse_id,
            delta=-item.quantity,
            movement_type=MovementType.SALE_DISPATCH,
            reference_id=so.so_number,
            user_id=user_id
        )

        db.flush()

        # Check whether available stock is below the reorder level
        product = db.query(Product).filter(
            Product.id == item.product_id
        ).first()

        if product:
            available_stock = (
                inv.quantity_on_hand - inv.quantity_reserved
            )

            if available_stock < product.reorder_level:

                recipients = db.query(User).filter(
                    User.is_active.is_(True),
                    User.role.in_([
                        UserRole.ADMIN,
                        UserRole.INVENTORY_MANAGER
                    ])
                ).all()

                for recipient in recipients:
                    bg_tasks.add_task(
                        send_email_background,
                        recipient.email,
                        f"Low Stock Alert: {product.name}",
                        (
                            "<h3>Low Stock Alert</h3>"
                            f"<p>Product: {product.name}</p>"
                            f"<p>SKU: {product.sku}</p>"
                            f"<p>Warehouse ID: {so.warehouse_id}</p>"
                            f"<p>Available stock: {available_stock}</p>"
                            f"<p>Reorder level: {product.reorder_level}</p>"
                        )
                    )

    # Update sales order details
    so.status = SOStatus.DISPATCHED
    so.courier_name = data.courier_name
    so.tracking_number = data.tracking_number
    so.dispatched_at = datetime.datetime.utcnow()

    log_audit(db, user_id, "DISPATCH", "SalesOrder", so.id)

    db.commit()
    db.refresh(so)

    # Send dispatch confirmation to the customer
    bg_tasks.add_task(
        send_email_background,
        so.customer.email,
        f"Order Dispatched: {so.so_number}",
        (
            f"<p>Dispatched via {so.courier_name}. "
            f"Tracking: {so.tracking_number}</p>"
        )
    )

    return so

def deliver_sales_order(db: Session, so_id: int, user_id: int) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).with_for_update().first()
    if not so or so.status != SOStatus.DISPATCHED:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Can only deliver Dispatched orders")
    so.status = SOStatus.DELIVERED
    so.delivered_at = datetime.datetime.utcnow()
    log_audit(db, user_id, "DELIVER", "SalesOrder", so.id)
    db.commit()
    db.refresh(so)
    return so

def cancel_sales_order(db: Session, so_id: int, user_id: int) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == so_id).with_for_update().first()
    if not so:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales order not found")
    if so.status in [SOStatus.DISPATCHED, SOStatus.DELIVERED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dispatched or Delivered orders cannot be cancelled")
    
    if so.status in [SOStatus.CONFIRMED, SOStatus.PICKED, SOStatus.PACKED]:
        for item in so.items:
            inv = db.query(Inventory).filter(
                Inventory.product_id == item.product_id,
                Inventory.warehouse_id == so.warehouse_id
            ).with_for_update().first()
            if inv:
                inv.quantity_reserved = max(0, inv.quantity_reserved - item.quantity)

    so.status = SOStatus.CANCELLED
    log_audit(db, user_id, "CANCEL", "SalesOrder", so.id)
    db.commit()
    db.refresh(so)
    return so
