from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class AccountSnapshot(Base):
    __tablename__ = 'account_snapshots'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    accounts_count = Column(Integer, nullable=False)
    total_market_value = Column(Float, nullable=False)
    total_cash_amount = Column(Float, nullable=False)
    accounts_info = Column(JSON, nullable=False)  # JSON containing detailed account information
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    positions = relationship("PositionSnapshot", back_populates="account_snapshot")

class PositionSnapshot(Base):
    __tablename__ = 'position_snapshots'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    total_value = Column(Float, nullable=False)
    cost_base_value = Column(Float, nullable=False)
    open_pl = Column(Float, nullable=False)
    position_info = Column(JSON, nullable=False)  # JSON containing detailed position information
    account_snapshot_id = Column(Integer, ForeignKey('account_snapshots.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account_snapshot = relationship("AccountSnapshot", back_populates="positions") 