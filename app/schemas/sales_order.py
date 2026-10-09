from pydantic import BaseModel
from typing import List, Optional
import datetime
from app.utils.enums import SOStatus

class SOItemCreate(BaseModel):
    product_id: int
    quantity: int

class SOCreate(BaseModel):
    customer_id: int
    warehouse_id: int
    items: List[SOItemCreate]

class SODispatch(BaseModel):
    courier_name: str
    tracking_number: str

class SOItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    line_total: float

    class Config:
        from_attributes = True

class SOResponse(BaseModel):
    id: int
    so_number: str
    customer_id: int
    warehouse_id: int
    subtotal: float
    tax_amount: float
    grand_total: float
    status: SOStatus
    courier_name: Optional[str] = None
    tracking_number: Optional[str] = None
    dispatched_at: Optional[datetime.datetime] = None
    delivered_at: Optional[datetime.datetime] = None
    items: List[SOItemResponse]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
