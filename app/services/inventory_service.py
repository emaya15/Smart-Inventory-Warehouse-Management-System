from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
import datetime
from app.models.inventory import Inventory
from app.models.stock_movement import StockMovement
from app.models.warehouse import Warehouse
from app.models.batch import Batch
from app.utils.enums import MovementType

def get_or_create_inventory(db: Session, product_id: int, warehouse_id: int) -> Inventory:
    inv = db.query(Inventory).filter(
        Inventory.product_id == product_id,
        Inventory.warehouse_id == warehouse_id
    ).with_for_update().first()

    if not inv:
        wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
        if not wh or not wh.is_active:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warehouse inactive or non-existent")
        inv = Inventory(product_id=product_id, warehouse_id=warehouse_id, quantity_on_hand=0, quantity_reserved=0)
        db.add(inv)
        db.flush()
    return inv

def change_inventory_stock(
    db: Session,
    product_id: int,
    warehouse_id: int,
    delta: int,
    movement_type: MovementType,
    reference_id: str,
    user_id: int
) -> Inventory:
    wh = db.query(Warehouse).filter(Warehouse.id == warehouse_id).first()
    if not wh or not wh.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warehouse inactive")
        
    inv = get_or_create_inventory(db, product_id, warehouse_id)

    if delta > 0:
        total_wh_stock = db.query(func.sum(Inventory.quantity_on_hand)).filter(Inventory.warehouse_id == warehouse_id).scalar() or 0
        if total_wh_stock + delta > wh.capacity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Warehouse capacity exceeded")

    if inv.quantity_on_hand + delta < 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient stock on hand; cannot become negative")

    inv.quantity_on_hand += delta
    db.flush()

    mv = StockMovement(
        product_id=product_id,
        warehouse_id=warehouse_id,
        movement_type=movement_type,
        quantity=delta,
        reference_id=reference_id,
        balance_after=inv.quantity_on_hand,
        performed_by=user_id
    )
    db.add(mv)
    return inv
