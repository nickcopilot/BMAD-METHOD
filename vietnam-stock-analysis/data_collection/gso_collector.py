"""
GSO Economic Data Collector
Collects Vietnamese economic indicators from General Statistics Office (GSO.gov.vn)
"""

import logging
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import re
import sys
import os

# Add shared module to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.models.database import DatabaseManager, EconomicIndicator, get_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GSOCollector:
    """Collects economic data from GSO.gov.vn"""

    def __init__(self, db_manager: Optional[DatabaseManager] = None):
        self.db = db_manager or get_db()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Disable SSL verification to handle certificate issues
        self.session.verify = False
        # Suppress SSL warnings
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_gdp_data(self) -> List[EconomicIndicator]:
        """Collect GDP growth data from GSO"""
        indicators = []

        try:
            # GSO GDP data URLs (these may need adjustment based on actual GSO structure)
            gdp_urls = [
                'https://www.gso.gov.vn/en/data-and-statistics/2024/04/gross-domestic-product-in-the-first-quarter-of-2024/',
                'https://www.gso.gov.vn/en/data-and-statistics/2024/07/gross-domestic-product-in-the-second-quarter-of-2024/',
                'https://www.gso.gov.vn/en/data-and-statistics/2024/10/gross-domestic-product-in-the-third-quarter-of-2024/'
            ]

            for url in gdp_urls:
                try:
                    response = self.session.get(url, timeout=30)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        # Extract GDP growth rate (this is a simplified example)
                        # Real implementation would need to parse GSO's specific HTML structure
                        text_content = soup.get_text()

                        # Look for GDP growth patterns
                        gdp_pattern = r'(\d+\.\d+)%?\s*(?:GDP|growth|tăng trưởng)'
                        matches = re.findall(gdp_pattern, text_content, re.IGNORECASE)

                        if matches:
                            # Extract quarter/year from URL
                            quarter_match = re.search(r'quarter-of-(\d{4})', url)
                            if quarter_match:
                                year = quarter_match.group(1)
                                quarter = url.split('quarter-of')[0].split('-')[-2]
                                quarter_map = {'first': 'Q1', 'second': 'Q2', 'third': 'Q3', 'fourth': 'Q4'}
                                period = f"{quarter_map.get(quarter.lower(), 'Q1')}-{year}"

                                indicator = EconomicIndicator(
                                    indicator_code='GDP_GROWTH',
                                    indicator_name='GDP Growth Rate',
                                    period=period,
                                    value=float(matches[0]),
                                    unit='percent',
                                    source='GSO',
                                    category='growth',
                                    release_date=datetime.now().strftime('%Y-%m-%d'),
                                    created_at=datetime.now().isoformat()
                                )
                                indicators.append(indicator)
                                logger.info(f"Collected GDP growth: {matches[0]}% for {period}")

                except Exception as e:
                    logger.error(f"Error processing GDP URL {url}: {e}")

        except Exception as e:
            logger.error(f"Error collecting GDP data: {e}")

        return indicators

    def get_inflation_data(self) -> List[EconomicIndicator]:
        """Collect CPI inflation data from GSO"""
        indicators = []

        try:
            # GSO CPI data URL (example - needs adjustment for actual GSO structure)
            cpi_url = 'https://www.gso.gov.vn/en/data-and-statistics/2024/11/consumer-price-index-in-october-2024/'

            response = self.session.get(cpi_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()

                # Look for inflation/CPI patterns
                inflation_patterns = [
                    r'(\d+\.\d+)%?\s*(?:inflation|CPI|consumer price)',
                    r'tăng\s*(\d+\.\d+)%',  # Vietnamese pattern
                ]

                for pattern in inflation_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        # Extract month/year from URL or content
                        month_match = re.search(r'(\w+)-(\d{4})', cpi_url)
                        if month_match:
                            month, year = month_match.groups()
                            period = f"{year}-{month}"

                            indicator = EconomicIndicator(
                                indicator_code='CPI_INFLATION',
                                indicator_name='Consumer Price Index Inflation',
                                period=period,
                                value=float(matches[0]),
                                unit='percent',
                                source='GSO',
                                category='inflation',
                                release_date=datetime.now().strftime('%Y-%m-%d'),
                                created_at=datetime.now().isoformat()
                            )
                            indicators.append(indicator)
                            logger.info(f"Collected CPI inflation: {matches[0]}% for {period}")
                        break

        except Exception as e:
            logger.error(f"Error collecting CPI data: {e}")

        return indicators

    def get_trade_data(self) -> List[EconomicIndicator]:
        """Collect trade balance data from GSO"""
        indicators = []

        try:
            # GSO trade data URL (example)
            trade_url = 'https://www.gso.gov.vn/en/data-and-statistics/2024/11/import-export-in-october-2024/'

            response = self.session.get(trade_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()

                # Look for export/import values
                trade_patterns = [
                    r'export[^0-9]*(\d+(?:\.\d+)?)\s*billion',
                    r'import[^0-9]*(\d+(?:\.\d+)?)\s*billion',
                ]

                for i, pattern in enumerate(trade_patterns):
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        indicator_type = 'EXPORTS' if i == 0 else 'IMPORTS'
                        period = datetime.now().strftime('%Y-%m')

                        indicator = EconomicIndicator(
                            indicator_code=f'TRADE_{indicator_type}',
                            indicator_name=f'Monthly {indicator_type.title()}',
                            period=period,
                            value=float(matches[0]),
                            unit='billion_usd',
                            source='GSO',
                            category='trade',
                            release_date=datetime.now().strftime('%Y-%m-%d'),
                            created_at=datetime.now().isoformat()
                        )
                        indicators.append(indicator)
                        logger.info(f"Collected {indicator_type}: ${matches[0]}B for {period}")

        except Exception as e:
            logger.error(f"Error collecting trade data: {e}")

        return indicators

    def get_state_bank_data(self) -> List[EconomicIndicator]:
        """Collect monetary policy data from State Bank of Vietnam"""
        indicators = []

        try:
            # State Bank of Vietnam interest rate data
            sbv_url = 'https://www.sbv.gov.vn/webcenter/portal/en/home/rm/ir'

            response = self.session.get(sbv_url, timeout=30)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                text_content = soup.get_text()

                # Look for interest rate patterns
                rate_patterns = [
                    r'(\d+\.\d+)%?\s*(?:interest rate|refinancing rate|base rate)',
                    r'lãi suất\s*(\d+\.\d+)%',  # Vietnamese pattern
                ]

                for pattern in rate_patterns:
                    matches = re.findall(pattern, text_content, re.IGNORECASE)
                    if matches:
                        period = datetime.now().strftime('%Y-%m')

                        indicator = EconomicIndicator(
                            indicator_code='INTEREST_RATE',
                            indicator_name='Central Bank Interest Rate',
                            period=period,
                            value=float(matches[0]),
                            unit='percent',
                            source='SBV',
                            category='monetary',
                            release_date=datetime.now().strftime('%Y-%m-%d'),
                            created_at=datetime.now().isoformat()
                        )
                        indicators.append(indicator)
                        logger.info(f"Collected interest rate: {matches[0]}% for {period}")
                        break

        except Exception as e:
            logger.error(f"Error collecting State Bank data: {e}")

        return indicators

    def store_economic_indicators(self, indicators: List[EconomicIndicator]) -> Tuple[int, int]:
        """Store economic indicators in database"""
        success_count = 0
        error_count = 0

        for indicator in indicators:
            try:
                if self.db.insert_economic_indicator(indicator):
                    success_count += 1
                    logger.info(f"✓ Stored {indicator.indicator_code}: {indicator.value}")
                else:
                    error_count += 1
                    logger.error(f"✗ Failed to store {indicator.indicator_code}")

            except Exception as e:
                error_count += 1
                logger.error(f"✗ Failed to store {indicator.indicator_code}: {e}")

        return success_count, error_count

    def run_weekly_collection(self) -> Dict[str, int]:
        """Run the weekly economic data collection process"""
        logger.info("Starting weekly economic data collection...")

        results = {
            'gdp_indicators': 0,
            'inflation_indicators': 0,
            'trade_indicators': 0,
            'monetary_indicators': 0,
            'errors': 0
        }

        try:
            # Collect different types of economic data
            all_indicators = []

            # GDP data (quarterly)
            gdp_indicators = self.get_gdp_data()
            all_indicators.extend(gdp_indicators)
            results['gdp_indicators'] = len(gdp_indicators)

            # Inflation data (monthly)
            inflation_indicators = self.get_inflation_data()
            all_indicators.extend(inflation_indicators)
            results['inflation_indicators'] = len(inflation_indicators)

            # Trade data (monthly)
            trade_indicators = self.get_trade_data()
            all_indicators.extend(trade_indicators)
            results['trade_indicators'] = len(trade_indicators)

            # Monetary policy data (as needed)
            monetary_indicators = self.get_state_bank_data()
            all_indicators.extend(monetary_indicators)
            results['monetary_indicators'] = len(monetary_indicators)

            # Store all indicators
            if all_indicators:
                success_count, error_count = self.store_economic_indicators(all_indicators)
                results['errors'] = error_count

            logger.info("Weekly economic data collection completed")
            logger.info(f"Results: {results}")

        except Exception as e:
            logger.error(f"Error in weekly collection: {e}")
            results['errors'] += 1

        return results

    def test_connection(self) -> bool:
        """Test connection to GSO website"""
        try:
            response = self.session.get('https://www.gso.gov.vn', timeout=10)
            if response.status_code == 200:
                logger.info("✓ GSO connection successful")
                return True
            else:
                logger.error(f"✗ GSO connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"✗ GSO connection error: {e}")
            return False


def main():
    """Main function for testing the collector"""
    collector = GSOCollector()

    print("Testing GSO Economic Data Collector...")
    print("=" * 50)

    # Test connection
    if collector.test_connection():
        print("✓ Connection to GSO successful")

        # Test data collection
        print("\nTesting data collection...")

        # Test GDP data
        gdp_data = collector.get_gdp_data()
        print(f"GDP indicators collected: {len(gdp_data)}")

        # Test inflation data
        inflation_data = collector.get_inflation_data()
        print(f"Inflation indicators collected: {len(inflation_data)}")

        # Test trade data
        trade_data = collector.get_trade_data()
        print(f"Trade indicators collected: {len(trade_data)}")

        # Test State Bank data
        monetary_data = collector.get_state_bank_data()
        print(f"Monetary indicators collected: {len(monetary_data)}")

    else:
        print("✗ Cannot connect to GSO, skipping tests")


if __name__ == "__main__":
    main()