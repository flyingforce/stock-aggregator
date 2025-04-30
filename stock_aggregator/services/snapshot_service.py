from datetime import date
from ..db.repository import Repository
from ..config import Config

class SnapshotService:
    def __init__(self, config: Config):
        self.repository = Repository(config.DATABASE_URL)
    
    def save_account_snapshot(self, date: date, cash_total: float, cost_basis: float,
                            accounts_count: int, market_value: float, open_pl: float,
                            account_info: dict):
        """Save an account snapshot to the database"""
        return self.repository.save_account_snapshot(
            date=date,
            cash_total=cash_total,
            cost_basis=cost_basis,
            accounts_count=accounts_count,
            market_value=market_value,
            open_pl=open_pl,
            account_info=account_info
        )
    
    def save_position_snapshot(self, date: date, cost_basis: float, market_value: float,
                             open_pl: float, position_info: dict):
        """Save a position snapshot to the database"""
        return self.repository.save_position_snapshot(
            date=date,
            cost_basis=cost_basis,
            market_value=market_value,
            open_pl=open_pl,
            position_info=position_info
        )
    
    def get_account_snapshot(self, date: date):
        """Get an account snapshot from the database"""
        return self.repository.get_account_snapshot(date)
    
    def get_position_snapshot(self, date: date):
        """Get a position snapshot from the database"""
        return self.repository.get_position_snapshot(date)
    
    def get_account_snapshots(self, start_date: date, end_date: date):
        """Get account snapshots from the database"""
        return self.repository.get_account_snapshots(start_date, end_date)
    
    def get_position_snapshots(self, start_date: date, end_date: date):
        """Get position snapshots from the database"""
        return self.repository.get_position_snapshots(start_date, end_date) 