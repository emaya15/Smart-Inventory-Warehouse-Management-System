from pydantic import BaseModel
from typing import List, Optional
import datetime
from app.utils.enums import ReturnStatus, ReturnCondition

class ReturnItemCreate(BaseModel):
    product_id: int
    quantity: int
    condition_type: ReturnCondition = ReturnCondition.GOOD
    reason: str

class ReturnCreate(BaseModel):
    items: List[ReturnItemCreate]

class ReturnItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    condition_type: ReturnCondition
    reason: str

    class Config:
        from_attributes = True

class ReturnResponse(BaseModel):
    id: int
    return_number: str
    sales_order_id: int
    status: ReturnStatus
    refund_amount: float
    rejection_reason: Optional[str] = None
    items: List[ReturnItemResponse]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
