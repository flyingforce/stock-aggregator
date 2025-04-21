from typing import Dict, Any
from datetime import datetime, timedelta
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from ..db.repository import DatabaseRepository
from .brokers_data import BrokersDataService
from ..config import Config

logger = logging.getLogger(__name__)

class SnapshotService:
    def __init__(self):
        self.config = Config()
        self.db_repository = DatabaseRepository(self.config.config['database'])
        self.brokers_service = BrokersDataService()
        self.scheduler = BackgroundScheduler()
        self._setup_scheduler()
    
    def _setup_scheduler(self):
        """Setup the scheduler to run snapshot generation at specified intervals"""
        # Get schedule configuration
        schedule_config = self.config.config.get('snapshot_schedule', {})
        hour = schedule_config.get('hour', 16)  # Default to 4 PM
        minute = schedule_config.get('minute', 0)  # Default to 0 minutes
        
        # Add the job to run daily at the specified time
        self.scheduler.add_job(
            self.generate_snapshot,
            CronTrigger(hour=hour, minute=minute),
            id='daily_snapshot',
            name='Generate daily portfolio snapshot',
            replace_existing=True
        )
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Snapshot service scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        logger.info("Snapshot service scheduler stopped")
    
    def generate_snapshot(self):
        """Generate and store a snapshot of the current portfolio state"""
        try:
            # Get current accounts and positions data
            accounts = self.brokers_service.get_accounts()
            positions_data = self.brokers_service.get_positions()
            
            # Calculate total cash amount
            total_cash = sum(
                account['balance'] 
                for account in accounts 
                if account.get('type', '').lower() == 'cash'
            )
            
            # Prepare account snapshot data
            account_snapshot = {
                'accounts_count': len(accounts),
                'total_market_value': positions_data['total_market_value'],
                'total_cash_amount': total_cash,
                'accounts_info': accounts
            }
            
            # Save account snapshot and get its ID
            account_snapshot_id = self.db_repository.save_account_snapshot(account_snapshot)
            
            # Prepare position snapshot data
            position_snapshot = {
                'total_value': positions_data['total_market_value'],
                'cost_base_value': positions_data['total_market_value'] - positions_data['total_unrealized_pl'],
                'open_pl': positions_data['total_unrealized_pl'],
                'position_info': positions_data['positions_by_type']
            }
            
            # Save position snapshot
            self.db_repository.save_position_snapshot(position_snapshot, account_snapshot_id)
            
            logger.info("Successfully generated and stored portfolio snapshot")
            
        except Exception as e:
            logger.error(f"Error generating snapshot: {str(e)}")
            raise
    
    def cleanup_old_snapshots(self, days_to_keep: int = 30):
        """Clean up snapshots older than the specified number of days"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            self.db_repository.delete_old_snapshots(cutoff_date)
            logger.info(f"Cleaned up snapshots older than {days_to_keep} days")
        except Exception as e:
            logger.error(f"Error cleaning up old snapshots: {str(e)}")
            raise 