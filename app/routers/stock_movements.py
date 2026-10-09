from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.stock_movement import StockMovement
from app.schemas.stock_movement import StockMovementResponse
from app.dependencies import get_current_active_user

router = APIRouter(prefix="/stock-movements", tags=["Stock Movements"])

@router.get("", response_model=List[StockMovementResponse])
def get_stock_movements(
    product_id: Optional[int] = None,
    warehouse_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user = Depends(get_current_active_user)
):
    q = db.query(StockMovement)
    if product_id:
        q = q.filter(StockMovement.product_id == product_id)
    if warehouse_id:
        q = q.filter(StockMovement.warehouse_id == warehouse_id)
    return q.order_by(StockMovement.created_at.desc()).offset(skip).limit(limit).all()
