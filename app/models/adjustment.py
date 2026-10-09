from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import datetime
from app.database import Base
from app.utils.enums import AdjustmentReason, AdjustmentStatus

class Adjustment(Base):
    __tablename__ = "adjustments"

    id = Column(Integer, primary_key=True, index=True)
    adjustment_number = Column(String(50), unique=True, nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity_delta = Column(Integer, nullable=False)
    reason = Column(SQLEnum(AdjustmentReason), nullable=False)
    rejection_reason = Column(Text, nullable=True)
    status = Column(SQLEnum(AdjustmentStatus), default=AdjustmentStatus.PENDING, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    warehouse = relationship("Warehouse")
    product = relationship("Product")
