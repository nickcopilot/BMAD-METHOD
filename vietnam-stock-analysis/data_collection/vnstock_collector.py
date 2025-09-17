"""
VNStock Data Collector
Collects stock price, volume, and company data from vnstock API
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import pandas as pd
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.models.database import DatabaseManager, Stock, PriceData, FinancialData, get_db
from shared.utils.validators import validate_data_batch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VNStockCollector:
    """Collects data from vnstock API for Vietnamese stocks"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or get_db()
        self._vnstock = None

    @property
    def vnstock(self):
        """Lazy import vnstock to handle import errors gracefully"""
        if self._vnstock is None:
            try:
                from vnstock import Quote, Company, Finance
                self._vnstock = {
                    'Quote': Quote,
                    'Company': Company,
                    'Finance': Finance
                }
                logger.info("VNStock library loaded successfully")
            except ImportError as e:
                logger.error(f"Failed to import vnstock: {e}")
                raise ImportError("vnstock library not available. Install with: pip install vnstock")
        return self._vnstock

    def get_tracked_stocks(self) -> List[str]:
        """Get list of stock symbols we're tracking across 4 sectors"""
        target_stocks = {
            # Securities sector - top companies
            'securities': ['SSI', 'VCI', 'VND', 'HCM', 'SHS'],
            # Banking sector - major banks
            'banking': ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'ACB'],
            # Real Estate sector - leading developers
            'real_estate': ['VHM', 'VIC', 'VRE', 'NVL', 'KDH', 'DXG', 'PDR'],
            # Steel sector - major producers
            'steel': ['HPG', 'HSG', 'NKG', 'TLH', 'VGS']
        }

        all_symbols = []
        for sector_stocks in target_stocks.values():
            all_symbols.extend(sector_stocks)

        logger.info(f"Tracking {len(all_symbols)} stocks across 4 sectors")
        return all_symbols

    def collect_stock_info(self, symbol: str) -> Optional[Stock]:
        """Collect basic stock information from vnstock"""
        try:
            # Get company overview using new API
            company = self.vnstock['Company'](symbol=symbol)
            profile = company.overview()

            if profile is None or profile.empty:
                logger.warning(f"No profile data for {symbol}")
                return None

            # Map vnstock data to our Stock model
            stock_data = profile.iloc[0] if len(profile) > 0 else profile

            # Determine sector based on our tracking lists
            sector_mapping = {
                'SSI': 'securities', 'VCI': 'securities', 'VND': 'securities',
                'HCM': 'securities', 'SHS': 'securities',
                'VCB': 'banking', 'BID': 'banking', 'CTG': 'banking',
                'TCB': 'banking', 'MBB': 'banking', 'VPB': 'banking', 'ACB': 'banking',
                'VHM': 'real_estate', 'VIC': 'real_estate', 'VRE': 'real_estate',
                'NVL': 'real_estate', 'KDH': 'real_estate', 'DXG': 'real_estate', 'PDR': 'real_estate',
                'HPG': 'steel', 'HSG': 'steel', 'NKG': 'steel', 'TLH': 'steel', 'VGS': 'steel'
            }

            stock = Stock(
                symbol=symbol,
                name=stock_data.get('companyName', symbol),
                name_en=stock_data.get('companyNameEng', symbol),
                sector=sector_mapping.get(symbol, 'unknown'),
                exchange=stock_data.get('exchange', 'HOSE'),
                market_cap=float(stock_data.get('marketCap', 0)) if stock_data.get('marketCap') else 0.0,
                industry_group=stock_data.get('industry', ''),
                listing_date=stock_data.get('listingDate', ''),
                is_active=True,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )

            logger.info(f"Collected info for {symbol}: {stock.name}")
            return stock

        except Exception as e:
            logger.error(f"Error collecting stock info for {symbol}: {e}")
            return None

    def collect_price_data(self, symbol: str, start_date: str, end_date: str) -> List[PriceData]:
        """Collect historical price data for a stock"""
        try:
            # Get historical data using new API
            quote = self.vnstock['Quote'](symbol=symbol)
            price_df = quote.history(
                start=start_date,
                end=end_date,
                interval='1D'
            )

            if price_df is None or price_df.empty:
                logger.warning(f"No price data for {symbol} from {start_date} to {end_date}")
                return []

            price_data_list = []
            for _, row in price_df.iterrows():
                price_data = PriceData(
                    stock_symbol=symbol,
                    date=row.name.strftime('%Y-%m-%d') if hasattr(row.name, 'strftime') else str(row.name),
                    open=float(row.get('open', 0)),
                    high=float(row.get('high', 0)),
                    low=float(row.get('low', 0)),
                    close=float(row.get('close', 0)),
                    volume=int(row.get('volume', 0)),
                    value=float(row.get('value', 0)) if 'value' in row else float(row.get('close', 0)) * int(row.get('volume', 0)),
                    foreign_buy=float(row.get('foreign_buy', 0)) if 'foreign_buy' in row else 0.0,
                    foreign_sell=float(row.get('foreign_sell', 0)) if 'foreign_sell' in row else 0.0
                )
                price_data_list.append(price_data)

            logger.info(f"Collected {len(price_data_list)} price records for {symbol}")
            return price_data_list

        except Exception as e:
            logger.error(f"Error collecting price data for {symbol}: {e}")
            return []

    def collect_financial_data(self, symbol: str) -> List[FinancialData]:
        """Collect financial statement data for a stock"""
        try:
            # Get financial data using new API
            finance = self.vnstock['Finance'](symbol=symbol)
            financial_df = finance.ratio()

            if financial_df is None or financial_df.empty:
                logger.warning(f"No financial data for {symbol}")
                return []

            financial_data_list = []
            for _, row in financial_df.iterrows():
                # Extract period information
                period = row.get('period', '')
                year = row.get('year', '')
                quarter = row.get('quarter', '')

                # Determine period format
                if quarter and year:
                    period_str = f"Q{quarter}-{year}"
                    period_type = "quarterly"
                elif year:
                    period_str = str(year)
                    period_type = "annual"
                else:
                    continue  # Skip if no period info

                financial_data = FinancialData(
                    stock_symbol=symbol,
                    period=period_str,
                    period_type=period_type,
                    revenue=float(row.get('revenue', 0)) / 1e9,  # Convert to billions
                    profit=float(row.get('profit', 0)) / 1e9,   # Convert to billions
                    total_assets=float(row.get('totalAssets', 0)) / 1e9,
                    equity=float(row.get('equity', 0)) / 1e9,
                    debt=float(row.get('debt', 0)) / 1e9,
                    roe=float(row.get('roe', 0)),
                    roa=float(row.get('roa', 0)),
                    pe_ratio=float(row.get('pe', 0)),
                    pb_ratio=float(row.get('pb', 0)),
                    debt_equity=float(row.get('debtEquity', 0)),
                    report_date=row.get('reportDate', '')
                )
                financial_data_list.append(financial_data)

            logger.info(f"Collected {len(financial_data_list)} financial records for {symbol}")
            return financial_data_list

        except Exception as e:
            logger.error(f"Error collecting financial data for {symbol}: {e}")
            return []

    def update_stock_database(self, symbols: Optional[List[str]] = None) -> Tuple[int, int]:
        """Update database with latest stock information"""
        if symbols is None:
            symbols = self.get_tracked_stocks()

        success_count = 0
        error_count = 0

        for symbol in symbols:
            try:
                # Collect stock info
                stock = self.collect_stock_info(symbol)
                if stock:
                    # Validate stock data
                    stock_dict = {
                        'symbol': stock.symbol,
                        'name': stock.name,
                        'sector': stock.sector,
                        'exchange': stock.exchange,
                        'market_cap': stock.market_cap
                    }

                    valid_data, validation_errors = validate_data_batch([stock_dict], 'stock_data')

                    if valid_data and self.db.insert_stock(stock):
                        success_count += 1
                        logger.info(f"✓ Updated stock info for {symbol}")
                    else:
                        error_count += 1
                        if validation_errors:
                            logger.error(f"✗ Validation failed for {symbol}: {validation_errors}")
                        else:
                            logger.error(f"✗ Failed to insert stock info for {symbol}")
                else:
                    error_count += 1
                    logger.error(f"✗ Failed to collect stock info for {symbol}")

            except Exception as e:
                error_count += 1
                logger.error(f"✗ Exception updating {symbol}: {e}")

        logger.info(f"Stock update complete: {success_count} success, {error_count} errors")
        return success_count, error_count

    def update_price_database(self, symbols: Optional[List[str]] = None, days_back: int = 30) -> Tuple[int, int]:
        """Update database with recent price data"""
        if symbols is None:
            symbols = self.get_tracked_stocks()

        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

        success_count = 0
        error_count = 0

        for symbol in symbols:
            try:
                # Collect price data
                price_data_list = self.collect_price_data(symbol, start_date, end_date)

                # Store in database
                for price_data in price_data_list:
                    if self.db.insert_price_data(price_data):
                        success_count += 1
                    else:
                        error_count += 1

                logger.info(f"✓ Updated price data for {symbol} ({len(price_data_list)} records)")

            except Exception as e:
                error_count += 1
                logger.error(f"✗ Exception updating price data for {symbol}: {e}")

        logger.info(f"Price update complete: {success_count} records, {error_count} errors")
        return success_count, error_count

    def run_daily_collection(self) -> Dict[str, int]:
        """Run the daily data collection process"""
        logger.info("Starting daily data collection...")

        results = {
            'stocks_updated': 0,
            'stocks_errors': 0,
            'price_records': 0,
            'price_errors': 0
        }

        # Update stock information (weekly is sufficient)
        if datetime.now().weekday() == 0:  # Monday
            stocks_success, stocks_errors = self.update_stock_database()
            results['stocks_updated'] = stocks_success
            results['stocks_errors'] = stocks_errors

        # Update price data (daily)
        price_success, price_errors = self.update_price_database(days_back=7)
        results['price_records'] = price_success
        results['price_errors'] = price_errors

        logger.info("Daily data collection completed")
        logger.info(f"Results: {results}")

        return results


def main():
    """Main function for testing the collector"""
    collector = VNStockCollector()

    # Test with a few stocks
    test_symbols = ['VCB', 'HPG', 'VHM']

    print("Testing VNStock Collector...")
    print("=" * 50)

    # Test stock info collection
    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")
        stock = collector.collect_stock_info(symbol)
        if stock:
            print(f"  ✓ Info: {stock.name} ({stock.sector})")
        else:
            print(f"  ✗ Failed to get info")

    # Test price data collection
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

    for symbol in test_symbols:
        price_data = collector.collect_price_data(symbol, start_date, end_date)
        print(f"  ✓ Price data: {len(price_data)} records")


if __name__ == "__main__":
    main()