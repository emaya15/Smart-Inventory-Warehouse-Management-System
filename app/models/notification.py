from sqlalchemy import Column, Integer, String, Text, DateTime
import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    recipient_email = Column(String(150), nullable=False)
    subject = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), default="SENT", nullable=False)
    sent_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
