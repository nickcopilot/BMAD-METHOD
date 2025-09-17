"""
Data Collection Scheduler
Manages automated daily and weekly data collection from Vietnamese sources
"""

import logging
from datetime import datetime, time
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from vnstock_collector import VNStockCollector
from gso_collector import GSOCollector
from shared.models.database import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DataCollectionScheduler:
    """Manages scheduled data collection tasks"""

    def __init__(self):
        self.scheduler = BlockingScheduler(timezone=pytz.timezone('Asia/Ho_Chi_Minh'))
        self.vnstock_collector = VNStockCollector()
        self.gso_collector = GSOCollector()
        self.db = get_db()

    def daily_stock_collection(self):
        """
        Daily stock data collection - runs after Vietnamese market close
        Vietnamese market hours: 9:00 AM - 11:30 AM and 1:00 PM - 3:00 PM ICT
        """
        logger.info("=== Starting Daily Stock Data Collection ===")

        try:
            # Run daily collection
            results = self.vnstock_collector.run_daily_collection()

            # Log results
            logger.info(f"Daily collection completed:")
            logger.info(f"  - Stocks updated: {results.get('stocks_updated', 0)}")
            logger.info(f"  - Stock errors: {results.get('stocks_errors', 0)}")
            logger.info(f"  - Price records: {results.get('price_records', 0)}")
            logger.info(f"  - Price errors: {results.get('price_errors', 0)}")

            # Send alert if too many errors
            total_errors = results.get('stocks_errors', 0) + results.get('price_errors', 0)
            if total_errors > 5:
                logger.warning(f"High error count in daily collection: {total_errors} errors")

        except Exception as e:
            logger.error(f"Critical error in daily stock collection: {e}")

        logger.info("=== Daily Stock Data Collection Complete ===")

    def weekly_economic_collection(self):
        """
        Weekly economic data collection - runs Monday mornings
        """
        logger.info("=== Starting Weekly Economic Data Collection ===")

        try:
            # Run weekly collection
            results = self.gso_collector.run_weekly_collection()

            # Log results
            logger.info(f"Weekly collection completed:")
            logger.info(f"  - GDP indicators: {results.get('gdp_indicators', 0)}")
            logger.info(f"  - Inflation indicators: {results.get('inflation_indicators', 0)}")
            logger.info(f"  - Trade indicators: {results.get('trade_indicators', 0)}")
            logger.info(f"  - Monetary indicators: {results.get('monetary_indicators', 0)}")
            logger.info(f"  - Errors: {results.get('errors', 0)}")

            # Send alert if errors occurred
            if results.get('errors', 0) > 0:
                logger.warning(f"Errors in weekly economic collection: {results.get('errors', 0)}")

        except Exception as e:
            logger.error(f"Critical error in weekly economic collection: {e}")

        logger.info("=== Weekly Economic Data Collection Complete ===")

    def test_data_collection(self):
        """Test collection function for development"""
        logger.info("=== Running Test Data Collection ===")

        try:
            # Test with a few symbols
            test_symbols = ['VCB', 'HPG', 'VHM']

            # Test stock data collection
            logger.info("Testing stock data collection...")
            stock_results = self.vnstock_collector.update_stock_database(test_symbols)
            logger.info(f"Stock test results: {stock_results}")

            # Test price data collection
            logger.info("Testing price data collection...")
            price_results = self.vnstock_collector.update_price_database(test_symbols, days_back=7)
            logger.info(f"Price test results: {price_results}")

            # Test economic data collection
            logger.info("Testing economic data collection...")
            if self.gso_collector.test_connection():
                economic_results = self.gso_collector.run_weekly_collection()
                logger.info(f"Economic test results: {economic_results}")
            else:
                logger.warning("Cannot connect to GSO, skipping economic test")

        except Exception as e:
            logger.error(f"Error in test collection: {e}")

        logger.info("=== Test Data Collection Complete ===")

    def setup_schedules(self):
        """Setup all scheduled jobs"""
        logger.info("Setting up data collection schedules...")

        # Daily stock data collection - runs at 6:00 PM ICT (after market close + buffer)
        self.scheduler.add_job(
            func=self.daily_stock_collection,
            trigger=CronTrigger(hour=18, minute=0, timezone='Asia/Ho_Chi_Minh'),
            id='daily_stock_collection',
            name='Daily Stock Data Collection',
            replace_existing=True
        )
        logger.info("✓ Scheduled daily stock collection at 18:00 ICT")

        # Weekly economic data collection - runs Monday at 9:00 AM ICT
        self.scheduler.add_job(
            func=self.weekly_economic_collection,
            trigger=CronTrigger(day_of_week='mon', hour=9, minute=0, timezone='Asia/Ho_Chi_Minh'),
            id='weekly_economic_collection',
            name='Weekly Economic Data Collection',
            replace_existing=True
        )
        logger.info("✓ Scheduled weekly economic collection on Monday 09:00 ICT")

        # Test collection (for development) - runs every hour
        # Remove this in production
        self.scheduler.add_job(
            func=self.test_data_collection,
            trigger=CronTrigger(minute=0, timezone='Asia/Ho_Chi_Minh'),
            id='test_collection',
            name='Test Data Collection',
            replace_existing=True
        )
        logger.info("✓ Scheduled test collection every hour (development only)")

    def start(self):
        """Start the scheduler"""
        logger.info("Starting data collection scheduler...")

        try:
            self.setup_schedules()

            # Print next job times
            logger.info("Scheduled jobs:")
            for job in self.scheduler.get_jobs():
                logger.info(f"  - {job.name}: next run at {job.next_run_time}")

            # Start scheduler
            logger.info("Scheduler started. Press Ctrl+C to stop.")
            self.scheduler.start()

        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.scheduler.shutdown()
        except Exception as e:
            logger.error(f"Error starting scheduler: {e}")
            raise

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.scheduler.shutdown()

    def run_now(self, job_name: str):
        """Run a specific job immediately"""
        if job_name == 'daily_stock':
            self.daily_stock_collection()
        elif job_name == 'weekly_economic':
            self.weekly_economic_collection()
        elif job_name == 'test':
            self.test_data_collection()
        else:
            logger.error(f"Unknown job: {job_name}")


def main():
    """Main function for running the scheduler"""
    import argparse

    parser = argparse.ArgumentParser(description='Vietnam Stock Analysis Data Collection Scheduler')
    parser.add_argument('--run-now', choices=['daily_stock', 'weekly_economic', 'test'],
                       help='Run a specific job immediately instead of starting scheduler')
    parser.add_argument('--test-mode', action='store_true',
                       help='Run in test mode with more frequent collections')

    args = parser.parse_args()

    scheduler = DataCollectionScheduler()

    if args.run_now:
        # Run specific job immediately
        scheduler.run_now(args.run_now)
    else:
        # Start scheduler
        if args.test_mode:
            logger.info("Running in test mode")

        scheduler.start()


if __name__ == "__main__":
    main()