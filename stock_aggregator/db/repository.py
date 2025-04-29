from datetime import date
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from .models import Base, Account, Position

class Repository:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_account_snapshot(self, date: date, cash_total: float, cost_basis: float,
                            accounts_count: int, market_value: float, open_pl: float,
                            account_info: dict):
        """Save an account snapshot for a specific date"""
        session = self.Session()
        try:
            # Delete existing snapshot for this date if it exists
            session.query(Account).filter(Account.date == date).delete()
            
            account = Account(
                date=date,
                cash_total=cash_total,
                cost_basis=cost_basis,
                accounts_count=accounts_count,
                market_value=market_value,
                open_pl=open_pl,
                account_info=account_info
            )
            session.add(account)
            session.commit()
            return account
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def save_position_snapshot(self, date: date, cost_basis: float, market_value: float,
                             open_pl: float, position_info: dict):
        """Save a position snapshot for a specific date"""
        session = self.Session()
        try:
            # Delete existing snapshot for this date if it exists
            session.query(Position).filter(Position.date == date).delete()
            
            position = Position(
                date=date,
                cost_basis=cost_basis,
                market_value=market_value,
                open_pl=open_pl,
                position_info=position_info
            )
            session.add(position)
            session.commit()
            return position
        except SQLAlchemyError as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_account_snapshot(self, date: date):
        """Get an account snapshot for a specific date"""
        session = self.Session()
        try:
            return session.query(Account).filter(Account.date == date).first()
        finally:
            session.close()
    
    def get_position_snapshot(self, date: date):
        """Get a position snapshot for a specific date"""
        session = self.Session()
        try:
            return session.query(Position).filter(Position.date == date).first()
        finally:
            session.close()
    
    def get_account_snapshots(self, start_date: date, end_date: date):
        """Get account snapshots for a date range"""
        session = self.Session()
        try:
            return session.query(Account).filter(
                Account.date.between(start_date, end_date)
            ).all()
        finally:
            session.close()
    
    def get_position_snapshots(self, start_date: date, end_date: date):
        """Get position snapshots for a date range"""
        session = self.Session()
        try:
            return session.query(Position).filter(
                Position.date.between(start_date, end_date)
            ).all()
        finally:
            session.close()
    
    def get_available_dates(self):
        """Get all dates that have snapshots in the database"""
        session = self.Session()
        try:
            # Get dates from both account and position snapshots
            account_dates = session.query(Account.date).distinct().all()
            position_dates = session.query(Position.date).distinct().all()
            
            # Combine and sort dates
            all_dates = set([d[0] for d in account_dates + position_dates])
            return sorted(all_dates, reverse=True)
        finally:
            session.close() 