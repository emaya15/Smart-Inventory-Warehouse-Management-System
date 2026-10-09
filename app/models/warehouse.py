from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)
    warehouse_code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(150), nullable=False)
    city = Column(String(100), nullable=False)
    address = Column(Text, nullable=False)
    capacity = Column(Integer, nullable=False)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    manager = relationship("User", foreign_keys=[manager_id])
    staff_members = relationship("User", foreign_keys="User.assigned_warehouse_id", back_populates="assigned_warehouse")
    inventories = relationship("Inventory", back_populates="warehouse")
    batches = relationship("Batch", back_populates="warehouse")
