from pydantic import BaseModel
from typing import Optional
import datetime

class InventoryResponse(BaseModel):
    id: int
    product_id: int
    warehouse_id: int
    quantity_on_hand: int
    quantity_reserved: int
    quantity_available: int
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class BatchCreate(BaseModel):
    batch_number: str
    manufacturing_date: datetime.date
    expiry_date: datetime.date
    unit_cost: float
    quantity: int

class BatchResponse(BaseModel):
    id: int
    batch_number: str
    product_id: int
    warehouse_id: int
    quantity: int
    manufacturing_date: datetime.date
    expiry_date: datetime.date
    unit_cost: float
    is_active: bool

    class Config:
        from_attributes = True
