from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Clerk user ID
    items = Column(JSON)
    total_items = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 