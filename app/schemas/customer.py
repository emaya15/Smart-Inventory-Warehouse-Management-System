from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class CustomerBase(BaseModel):
    customer_code: str
    name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    credit_limit: float = 0.00
    is_active: Optional[bool] = True

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    credit_limit: Optional[float] = None
    is_active: Optional[bool] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True
