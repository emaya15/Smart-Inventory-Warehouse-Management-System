from pydantic import BaseModel
from typing import List, Optional
import datetime
from app.utils.enums import POStatus

class POItemCreate(BaseModel):
    product_id: int
    quantity_ordered: int
    unit_cost: float

class POItemReceive(BaseModel):
    product_id: int
    quantity_received: int
    batch_number: Optional[str] = None
    manufacturing_date: Optional[datetime.date] = None
    expiry_date: Optional[datetime.date] = None

class POCreate(BaseModel):
    supplier_id: int
    warehouse_id: int
    expected_delivery_date: Optional[datetime.date] = None
    items: List[POItemCreate]

class POItemResponse(BaseModel):
    id: int
    product_id: int
    quantity_ordered: int
    quantity_received: int
    unit_cost: float

    class Config:
        from_attributes = True

class POResponse(BaseModel):
    id: int
    po_number: str
    supplier_id: int
    warehouse_id: int
    expected_delivery_date: datetime.date
    received_at: Optional[datetime.datetime] = None
    total_amount: float
    status: POStatus
    items: List[POItemResponse]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
