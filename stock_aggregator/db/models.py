from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, JSON, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Account(Base):
    __tablename__ = 'accounts'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    cash_total = Column(Float, nullable=False)
    cost_basis = Column(Float, nullable=False)
    accounts_count = Column(Integer, nullable=False)
    market_value = Column(Float, nullable=False)
    open_pl = Column(Float, nullable=False)
    account_info = Column(JSON, nullable=False)
    
    # Create an index on date
    __table_args__ = (
        Index('idx_accounts_date', 'date'),
    )

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, nullable=False)
    cost_basis = Column(Float, nullable=False)
    market_value = Column(Float, nullable=False)
    open_pl = Column(Float, nullable=False)
    position_info = Column(JSON, nullable=False)
    
    # Create an index on date
    __table_args__ = (
        Index('idx_positions_date', 'date'),
    ) 