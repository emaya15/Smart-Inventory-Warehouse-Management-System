from pydantic import BaseModel
from typing import Optional
import datetime

class WarehouseBase(BaseModel):
    warehouse_code: str
    name: str
    city: str
    address: str
    capacity: int
    manager_id: Optional[int] = None
    is_active: Optional[bool] = True

class WarehouseCreate(WarehouseBase):
    pass

class WarehouseUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None
    capacity: Optional[int] = None
    manager_id: Optional[int] = None
    is_active: Optional[bool] = None

class WarehouseResponse(WarehouseBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
