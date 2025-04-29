from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
from .brokers_data import BrokersDataService

logger = logging.getLogger(__name__)

class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.brokers_data = BrokersDataService()
        self._setup_jobs()
    
    def _setup_jobs(self):
        """Setup scheduled jobs"""
        # Schedule daily position snapshot at 4:00 PM EST
        self.scheduler.add_job(
            self._run_daily_snapshot,
            trigger=CronTrigger(hour=16, minute=0, timezone='America/New_York'),
            id='daily_position_snapshot',
            name='Daily position snapshot',
            replace_existing=True
        )
    
    def _run_daily_snapshot(self):
        """Run the daily position snapshot"""
        try:
            logger.info(f"Running daily position snapshot at {datetime.now()}")
            self.brokers_data.get_positions()
            logger.info("Daily position snapshot completed successfully")
        except Exception as e:
            logger.error(f"Error running daily position snapshot: {str(e)}")
    
    def start(self):
        """Start the scheduler"""
        self.scheduler.start()
        logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()
        logger.info("Scheduler shut down") 