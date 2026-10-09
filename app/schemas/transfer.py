from pydantic import BaseModel
from typing import List, Optional
import datetime
from app.utils.enums import TransferStatus

class TransferItemCreate(BaseModel):
    product_id: int
    quantity: int

class TransferCreate(BaseModel):
    source_warehouse_id: int
    destination_warehouse_id: int
    items: List[TransferItemCreate]

class TransferItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    received_quantity: int

    class Config:
        from_attributes = True

class TransferResponse(BaseModel):
    id: int
    transfer_number: str
    source_warehouse_id: int
    destination_warehouse_id: int
    status: TransferStatus
    dispatched_at: Optional[datetime.datetime] = None
    received_at: Optional[datetime.datetime] = None
    items: List[TransferItemResponse]
    created_at: datetime.datetime

    class Config:
        from_attributes = True
