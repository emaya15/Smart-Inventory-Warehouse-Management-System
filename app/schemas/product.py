from pydantic import BaseModel, field_validator
from typing import Optional, Dict, List, Any
import datetime
from app.utils.enums import UnitType

class ProductBase(BaseModel):
    sku: str
    barcode: Optional[str] = None
    name: str
    category_id: int
    unit: UnitType = UnitType.PIECE
    cost_price: float
    selling_price: float
    reorder_level: int = 10
    reorder_quantity: int = 50
    

    @field_validator("selling_price")
    @classmethod
    def validate_prices(cls, v, values):
        return v

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    name: Optional[str] = None
    category_id: Optional[int] = None
    unit: Optional[UnitType] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    reorder_level: Optional[int] = None
    reorder_quantity: Optional[int] = None
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        from_attributes = True

class ProductDetailResponse(ProductResponse):
    total_stock_on_hand: int = 0
    total_stock_available: int = 0
    warehouse_stock: List[Dict[str, Any]] = []
