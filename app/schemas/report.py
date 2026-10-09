from pydantic import BaseModel
from typing import List, Optional

class DashboardResponse(BaseModel):
    total_products: int
    total_stock_value: float
    low_stock_count: int
    pending_purchase_orders: int
    pending_sales_orders: int
    today_dispatches: int

class LowStockItem(BaseModel):
    product_id: int
    sku: str
    name: str
    available_stock: int
    reorder_level: int
    suggested_reorder_quantity: int
    preferred_supplier: Optional[str] = None

class ExpiryDashboardResponse(BaseModel):
    already_expired_count: int
    expiring_in_7_days_count: int
    expiring_in_30_days_count: int

class InventoryHealthScore(BaseModel):
    warehouse_id: int
    warehouse_name: str
    health_score: float
    low_stock_items: int
    dead_stock_items: int
    expired_items: int
