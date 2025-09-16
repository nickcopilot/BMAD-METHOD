#!/usr/bin/env python3
"""
Automated Daily Vietnamese Stock Data Pipeline
Collects, processes, and updates stock data for production system
"""

import os
import sys
import logging
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import time
from typing import Dict, List, Optional
import schedule
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import our analysis systems
try:
    from smart_money_signal_system import SmartMoneySignalSystem
    from stock_universe_manager import VietnamStockUniverse
    from comprehensive_stock_reporter import ComprehensiveStockReporter
    import vnstock as vn
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/data_pipeline.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class VietnamStockDataPipeline:
    def __init__(self, config_file: str = "pipeline_config.json"):
        """Initialize the data pipeline"""

        # Create necessary directories
        os.makedirs('logs', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        os.makedirs('cache', exist_ok=True)

        # Load configuration
        self.config = self.load_config(config_file)

        # Initialize database
        self.db_path = self.config.get('database_path', 'data/vietnam_stocks.db')
        self.init_database()

        # Initialize analysis systems
        self.signal_system = SmartMoneySignalSystem()
        self.universe_manager = VietnamStockUniverse()
        self.reporter = ComprehensiveStockReporter()
        self.vnstock_client = vn.Vnstock()

        # Stock universe
        self.stock_list = self.get_stock_universe()

        # Pipeline status
        self.pipeline_status = {
            'last_run': None,
            'success_count': 0,
            'error_count': 0,
            'total_stocks': len(self.stock_list),
            'processing_time': 0
        }

        logger.info(f"Data pipeline initialized with {len(self.stock_list)} stocks")

    def load_config(self, config_file: str) -> Dict:
        """Load pipeline configuration"""
        default_config = {
            "database_path": "data/vietnam_stocks.db",
            "update_schedule": "09:00",  # 9 AM Vietnam time
            "batch_size": 10,
            "max_workers": 5,
            "retry_attempts": 3,
            "cache_ttl": 3600,  # 1 hour
            "alert_email": "admin@example.com",
            "enable_signals": True,
            "enable_comprehensive_analysis": True,
            "data_retention_days": 365
        }

        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                # Merge with defaults
                default_config.update(config)
            else:
                # Create default config file
                with open(config_file, 'w') as f:
                    json.dump(default_config, f, indent=2)
                logger.info(f"Created default config file: {config_file}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")

        return default_config

    def init_database(self):
        """Initialize SQLite database for storing data"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Create tables
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stock_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    date TEXT NOT NULL,
                    open_price REAL,
                    high_price REAL,
                    low_price REAL,
                    close_price REAL,
                    volume INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, date)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS signals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT NOT NULL,
                    signal_date TEXT NOT NULL,
                    signal_type TEXT NOT NULL,
                    original_score REAL,
                    adjusted_score REAL,
                    classification TEXT,
                    vietnamese_context TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(symbol, signal_date)
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS pipeline_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    stocks_processed INTEGER,
                    signals_generated INTEGER,
                    processing_time REAL,
                    errors TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise

    def get_stock_universe(self) -> List[str]:
        """Get comprehensive list of Vietnamese stocks to monitor"""

        # Core liquid stocks by sector
        stock_universe = {
            'Banking': ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'TPB', 'STB', 'ACB', 'VIB'],
            'Real Estate': ['VIC', 'VHM', 'NVL', 'DXG', 'KDH', 'HDG', 'CEO', 'DIG', 'IDC', 'IJC'],
            'Technology': ['FPT', 'CMG', 'ELC', 'ITD', 'SAM', 'VGI', 'NET', 'SZC'],
            'Steel': ['HPG', 'HSG', 'NKG', 'SMC', 'TLH', 'TVN', 'VIS'],
            'Oil_Gas': ['GAS', 'PLX', 'PVS', 'PVD', 'PVC', 'PVB', 'BSR'],
            'Food_Beverage': ['VNM', 'MSN', 'MCH', 'KDC', 'QNS', 'TNG', 'VHC'],
            'Retail': ['MWG', 'PNJ', 'DGW', 'FRT', 'VRE', 'BST'],
            'Airlines': ['HVN', 'VJC'],
            'Securities': ['SSI', 'VCI', 'VND', 'HCM', 'MBS', 'CTS'],
            'Healthcare': ['DHG', 'IMP', 'DBD', 'TNH', 'AMV'],
            'Manufacturing': ['REE', 'HAG', 'FLC', 'TDH', 'LCG']
        }

        # Flatten the dictionary to get all stocks
        all_stocks = []
        for sector_stocks in stock_universe.values():
            all_stocks.extend(sector_stocks)

        # Remove duplicates and sort
        return sorted(list(set(all_stocks)))

    def collect_stock_data(self, symbol: str) -> Optional[Dict]:
        """Collect data for a single stock"""
        try:
            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')

            # Get recent data (last 5 days to ensure we have latest)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=5)

            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is not None and not data.empty:
                # Get the most recent row
                latest = data.iloc[-1]

                return {
                    'symbol': symbol,
                    'date': latest['time'].strftime('%Y-%m-%d'),
                    'open_price': float(latest['open']),
                    'high_price': float(latest['high']),
                    'low_price': float(latest['low']),
                    'close_price': float(latest['close']),
                    'volume': int(latest['volume'])
                }
            else:
                logger.warning(f"No data available for {symbol}")
                return None

        except Exception as e:
            logger.error(f"Error collecting data for {symbol}: {e}")
            return None

    def generate_stock_signals(self, symbol: str) -> Optional[Dict]:
        """Generate signals for a stock"""
        try:
            # Get sector
            sector = self.universe_manager.classify_stock_sector(symbol)

            # Generate signals
            signals = self.signal_system.generate_smart_money_signals(symbol, sector)

            if 'error' not in signals:
                vn_context = signals.get('vietnamese_market_context', {})

                return {
                    'symbol': symbol,
                    'signal_date': datetime.now().strftime('%Y-%m-%d'),
                    'signal_type': 'BUY' if vn_context.get('adjusted_score', 0) >= 60 else 'HOLD',
                    'original_score': signals.get('composite_signal_score', {}).get('composite_score', 0),
                    'adjusted_score': vn_context.get('adjusted_score', 0),
                    'classification': vn_context.get('signal_classification', 'Hold Signal'),
                    'vietnamese_context': json.dumps(vn_context.get('vietnamese_context_notes', []))
                }
            else:
                logger.warning(f"Signal generation failed for {symbol}: {signals['error']}")
                return None

        except Exception as e:
            logger.error(f"Error generating signals for {symbol}: {e}")
            return None

    def process_batch(self, stocks: List[str]) -> Dict:
        """Process a batch of stocks"""
        batch_results = {
            'data_collected': 0,
            'signals_generated': 0,
            'errors': []
        }

        with ThreadPoolExecutor(max_workers=self.config['max_workers']) as executor:
            # Submit data collection tasks
            data_futures = {
                executor.submit(self.collect_stock_data, symbol): symbol
                for symbol in stocks
            }

            # Submit signal generation tasks
            signal_futures = {
                executor.submit(self.generate_stock_signals, symbol): symbol
                for symbol in stocks
            } if self.config['enable_signals'] else {}

            # Process data collection results
            for future in as_completed(data_futures):
                symbol = data_futures[future]
                try:
                    result = future.result()
                    if result:
                        self.save_stock_data(result)
                        batch_results['data_collected'] += 1
                    else:
                        batch_results['errors'].append(f"Data collection failed for {symbol}")
                except Exception as e:
                    batch_results['errors'].append(f"Data collection error for {symbol}: {e}")

            # Process signal generation results
            for future in as_completed(signal_futures):
                symbol = signal_futures[future]
                try:
                    result = future.result()
                    if result:
                        self.save_signal_data(result)
                        batch_results['signals_generated'] += 1
                    else:
                        batch_results['errors'].append(f"Signal generation failed for {symbol}")
                except Exception as e:
                    batch_results['errors'].append(f"Signal generation error for {symbol}: {e}")

        return batch_results

    def save_stock_data(self, data: Dict):
        """Save stock data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO stock_data
                (symbol, date, open_price, high_price, low_price, close_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['symbol'], data['date'], data['open_price'],
                data['high_price'], data['low_price'], data['close_price'], data['volume']
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving stock data: {e}")

    def save_signal_data(self, signal: Dict):
        """Save signal data to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO signals
                (symbol, signal_date, signal_type, original_score, adjusted_score, classification, vietnamese_context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                signal['symbol'], signal['signal_date'], signal['signal_type'],
                signal['original_score'], signal['adjusted_score'],
                signal['classification'], signal['vietnamese_context']
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving signal data: {e}")

    def run_daily_pipeline(self):
        """Run the complete daily data pipeline"""
        start_time = time.time()
        run_date = datetime.now().strftime('%Y-%m-%d')

        logger.info(f"Starting daily pipeline run for {run_date}")

        total_results = {
            'data_collected': 0,
            'signals_generated': 0,
            'errors': []
        }

        try:
            # Process stocks in batches
            batch_size = self.config['batch_size']
            for i in range(0, len(self.stock_list), batch_size):
                batch = self.stock_list[i:i + batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {batch}")

                batch_results = self.process_batch(batch)

                # Aggregate results
                total_results['data_collected'] += batch_results['data_collected']
                total_results['signals_generated'] += batch_results['signals_generated']
                total_results['errors'].extend(batch_results['errors'])

                # Brief pause between batches to avoid overwhelming the API
                time.sleep(2)

            processing_time = time.time() - start_time

            # Update pipeline status
            self.pipeline_status.update({
                'last_run': run_date,
                'success_count': total_results['data_collected'],
                'error_count': len(total_results['errors']),
                'processing_time': processing_time
            })

            # Save pipeline run record
            self.save_pipeline_run(run_date, 'SUCCESS', total_results, processing_time)

            logger.info(f"Pipeline completed successfully in {processing_time:.2f}s")
            logger.info(f"Data collected: {total_results['data_collected']}")
            logger.info(f"Signals generated: {total_results['signals_generated']}")
            logger.info(f"Errors: {len(total_results['errors'])}")

            # Clean up old data
            self.cleanup_old_data()

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Pipeline failed: {e}")

            total_results['errors'].append(f"Pipeline failure: {e}")
            self.save_pipeline_run(run_date, 'FAILURE', total_results, processing_time)

            # Send alert email if configured
            self.send_alert_email(f"Data pipeline failed: {e}")

    def save_pipeline_run(self, run_date: str, status: str, results: Dict, processing_time: float):
        """Save pipeline run record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO pipeline_runs
                (run_date, status, stocks_processed, signals_generated, processing_time, errors)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                run_date, status, results['data_collected'],
                results['signals_generated'], processing_time,
                json.dumps(results['errors'])
            ))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Error saving pipeline run: {e}")

    def cleanup_old_data(self):
        """Clean up old data based on retention policy"""
        try:
            retention_days = self.config['data_retention_days']
            cutoff_date = (datetime.now() - timedelta(days=retention_days)).strftime('%Y-%m-%d')

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Clean up old stock data
            cursor.execute('DELETE FROM stock_data WHERE date < ?', (cutoff_date,))

            # Clean up old signals
            cursor.execute('DELETE FROM signals WHERE signal_date < ?', (cutoff_date,))

            # Clean up old pipeline runs (keep longer - 30 days)
            pipeline_cutoff = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute('DELETE FROM pipeline_runs WHERE run_date < ?', (pipeline_cutoff,))

            conn.commit()
            conn.close()

            logger.info(f"Cleaned up data older than {retention_days} days")

        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")

    def send_alert_email(self, message: str):
        """Send alert email (placeholder - implement with actual email service)"""
        # TODO: Implement actual email sending
        logger.warning(f"ALERT: {message}")

    def get_pipeline_status(self) -> Dict:
        """Get current pipeline status"""
        return self.pipeline_status.copy()

    def get_latest_signals(self, limit: int = 10) -> List[Dict]:
        """Get latest signals from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT symbol, signal_date, signal_type, adjusted_score, classification
                FROM signals
                ORDER BY created_at DESC
                LIMIT ?
            ''', (limit,))

            results = cursor.fetchall()
            conn.close()

            return [
                {
                    'symbol': row[0],
                    'signal_date': row[1],
                    'signal_type': row[2],
                    'adjusted_score': row[3],
                    'classification': row[4]
                }
                for row in results
            ]

        except Exception as e:
            logger.error(f"Error getting latest signals: {e}")
            return []

    def start_scheduler(self):
        """Start the scheduled pipeline execution"""
        update_time = self.config['update_schedule']

        # Schedule daily run
        schedule.every().day.at(update_time).do(self.run_daily_pipeline)

        logger.info(f"Scheduler started. Daily pipeline will run at {update_time}")

        # Run scheduler in background
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute

        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()

        return scheduler_thread

def main():
    """Main function to run the data pipeline"""
    pipeline = VietnamStockDataPipeline()

    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'run':
            # Run immediately
            pipeline.run_daily_pipeline()
        elif sys.argv[1] == 'schedule':
            # Start scheduler
            print("Starting Vietnamese stock data pipeline scheduler...")
            pipeline.start_scheduler()

            # Keep the main thread alive
            try:
                while True:
                    time.sleep(60)
            except KeyboardInterrupt:
                print("Scheduler stopped.")
        elif sys.argv[1] == 'status':
            # Show status
            status = pipeline.get_pipeline_status()
            print(f"Pipeline Status: {json.dumps(status, indent=2)}")

            latest_signals = pipeline.get_latest_signals(5)
            print(f"Latest Signals: {json.dumps(latest_signals, indent=2)}")
        else:
            print("Usage: python data_pipeline.py [run|schedule|status]")
    else:
        print("Vietnamese Stock Data Pipeline")
        print("Usage: python data_pipeline.py [run|schedule|status]")
        print("  run      - Run pipeline immediately")
        print("  schedule - Start scheduled pipeline")
        print("  status   - Show pipeline status")

if __name__ == "__main__":
    main()