from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any
from .models import Base, AccountSnapshot, PositionSnapshot
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseRepository:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.engine = self._create_engine()
        self.Session = scoped_session(sessionmaker(bind=self.engine))
        self._create_tables()
    
    def _create_engine(self):
        """Create SQLAlchemy engine from configuration"""
        db_url = f"postgresql://{self.config['user']}:{self.config['password']}@{self.config['host']}:{self.config['port']}/{self.config['name']}"
        return create_engine(
            db_url,
            pool_size=self.config.get('pool_size', 5),
            max_overflow=self.config.get('max_overflow', 10),
            echo=self.config.get('echo', False)
        )
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            Base.metadata.create_all(self.engine)
        except SQLAlchemyError as e:
            logger.error(f"Error creating tables: {str(e)}")
            raise
    
    def save_account_snapshot(self, snapshot_data: Dict) -> None:
        """Save a new account snapshot"""
        session = self.Session()
        try:
            snapshot = AccountSnapshot(
                date=datetime.utcnow(),
                accounts_count=snapshot_data['accounts_count'],
                total_market_value=snapshot_data['total_market_value'],
                total_cash_amount=snapshot_data['total_cash_amount'],
                accounts_info=snapshot_data['accounts_info']
            )
            session.add(snapshot)
            session.commit()
            return snapshot.id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving account snapshot: {str(e)}")
            raise
        finally:
            session.close()
    
    def save_position_snapshot(self, snapshot_data: Dict, account_snapshot_id: int) -> None:
        """Save a new position snapshot"""
        session = self.Session()
        try:
            snapshot = PositionSnapshot(
                date=datetime.utcnow(),
                total_value=snapshot_data['total_value'],
                cost_base_value=snapshot_data['cost_base_value'],
                open_pl=snapshot_data['open_pl'],
                position_info=snapshot_data['position_info'],
                account_snapshot_id=account_snapshot_id
            )
            session.add(snapshot)
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error saving position snapshot: {str(e)}")
            raise
        finally:
            session.close()
    
    def get_account_snapshots(self, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get account snapshots within a date range"""
        session = self.Session()
        try:
            query = session.query(AccountSnapshot)
            if start_date:
                query = query.filter(AccountSnapshot.date >= start_date)
            if end_date:
                query = query.filter(AccountSnapshot.date <= end_date)
            snapshots = query.order_by(AccountSnapshot.date.desc()).all()
            return [snapshot.__dict__ for snapshot in snapshots]
        except SQLAlchemyError as e:
            logger.error(f"Error getting account snapshots: {str(e)}")
            return []
        finally:
            session.close()
    
    def get_position_snapshots(self, account_snapshot_id: int = None, start_date: datetime = None, end_date: datetime = None) -> List[Dict]:
        """Get position snapshots within a date range"""
        session = self.Session()
        try:
            query = session.query(PositionSnapshot)
            if account_snapshot_id:
                query = query.filter_by(account_snapshot_id=account_snapshot_id)
            if start_date:
                query = query.filter(PositionSnapshot.date >= start_date)
            if end_date:
                query = query.filter(PositionSnapshot.date <= end_date)
            snapshots = query.order_by(PositionSnapshot.date.desc()).all()
            return [snapshot.__dict__ for snapshot in snapshots]
        except SQLAlchemyError as e:
            logger.error(f"Error getting position snapshots: {str(e)}")
            return []
        finally:
            session.close()
    
    def delete_old_snapshots(self, before_date: datetime) -> None:
        """Delete snapshots older than the specified date"""
        session = self.Session()
        try:
            # Delete position snapshots first due to foreign key constraint
            session.query(PositionSnapshot).filter(PositionSnapshot.date < before_date).delete()
            session.query(AccountSnapshot).filter(AccountSnapshot.date < before_date).delete()
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Error deleting old snapshots: {str(e)}")
            raise
        finally:
            session.close() 