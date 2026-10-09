from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class SupplierBase(BaseModel):
    supplier_code: str
    name: str
    email: EmailStr
    phone: str
    gst_number: str
    address: str
    lead_time_days: int = 3
    is_active: Optional[bool] = True

class SupplierCreate(SupplierBase):
    pass

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    gst_number: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: Optional[int] = None
    is_active: Optional[bool] = None

class SupplierResponse(SupplierBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
