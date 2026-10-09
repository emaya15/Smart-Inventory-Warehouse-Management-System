from pydantic import BaseModel
from typing import Optional
import datetime
from app.utils.enums import AdjustmentReason, AdjustmentStatus

class AdjustmentCreate(BaseModel):
    warehouse_id: int
    product_id: int
    quantity_delta: int
    reason: AdjustmentReason

class AdjustmentResponse(BaseModel):
    id: int
    adjustment_number: str
    warehouse_id: int
    product_id: int
    quantity_delta: int
    reason: AdjustmentReason
    status: AdjustmentStatus
    rejection_reason: Optional[str] = None
    created_at: datetime.datetime

    class Config:
        from_attributes = True
