from pydantic import BaseModel
from typing import Optional
import datetime
from app.utils.enums import MovementType

class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    movement_type: MovementType
    quantity: int
    reference_id: str
    balance_after: int
    performed_by: Optional[int] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True
