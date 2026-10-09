from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Enum as SQLEnum, Text
from sqlalchemy.orm import relationship
import datetime
from app.database import Base
from app.utils.enums import ReturnStatus, ReturnCondition

class Return(Base):
    __tablename__ = "returns"

    id = Column(Integer, primary_key=True, index=True)
    return_number = Column(String(50), unique=True, nullable=False, index=True)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    status = Column(SQLEnum(ReturnStatus), default=ReturnStatus.REQUESTED, nullable=False)
    refund_amount = Column(Numeric(12, 2), default=0.00, nullable=False)
    rejection_reason = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    sales_order = relationship("SalesOrder", back_populates="returns")
    items = relationship("ReturnItem", back_populates="parent_return", cascade="all, delete-orphan")

class ReturnItem(Base):
    __tablename__ = "return_items"

    id = Column(Integer, primary_key=True, index=True)
    return_id = Column(Integer, ForeignKey("returns.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    condition_type = Column(SQLEnum(ReturnCondition), default=ReturnCondition.GOOD, nullable=False)
    reason = Column(String(255), nullable=False)

    parent_return = relationship("Return", back_populates="items")
    product = relationship("Product")
