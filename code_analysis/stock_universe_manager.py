#!/usr/bin/env python3
"""
Vietnam Stock Universe Manager
Discovers and manages all liquid Vietnamese stocks for analysis
Filters out penny stocks and low-liquidity names
"""

import vnstock as vn
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VietnamStockUniverse:
    def __init__(self):
        self.vnstock_client = vn.Vnstock()

        # Liquidity filters to exclude penny stocks
        self.liquidity_filters = {
            'min_price': 5000,              # Minimum 5,000 VND per share
            'min_avg_volume': 100000,       # Minimum 100K shares avg daily volume
            'min_market_cap': 500000000000, # Minimum 500B VND market cap (~$20M USD)
            'min_trading_days': 200,        # Must trade at least 200 days in last year
            'max_daily_volatility': 0.15    # Maximum 15% average daily volatility
        }

        # Vietnamese stock exchanges
        self.exchanges = ['HOSE', 'HNX', 'UPCOM']

        # Sector classification (enhanced)
        self.sector_mapping = {
            # Banking & Financial Services
            'Banks': ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'TPB', 'STB', 'EIB', 'ACB', 'VIB', 'SHB', 'MSB', 'OCB', 'LPB'],
            'Securities': ['SSI', 'VCI', 'VND', 'HCM', 'MAS', 'FTS', 'CTS', 'APS', 'ORS', 'IVS', 'VDS', 'BVS'],
            'Insurance': ['BIC', 'BMI', 'MIG', 'PVI', 'VNR'],

            # Real Estate & Construction
            'Real_Estate': ['VHM', 'VIC', 'NVL', 'DXG', 'KDH', 'HDG', 'NBB', 'CEO', 'IJC', 'PDR', 'DIG', 'TCH'],
            'Construction': ['CTD', 'HBC', 'ROS', 'TV2', 'C4G', 'FCN', 'HUT', 'PC1', 'CTI', 'SCS'],

            # Manufacturing & Materials
            'Steel': ['HPG', 'HSG', 'NKG', 'TLH', 'SMC', 'TVN', 'POM', 'VCA', 'DTL'],
            'Chemicals': ['DPM', 'CSV', 'BFC', 'DCM', 'LAS', 'DDV', 'PAC', 'TNC', 'DAP'],
            'Textiles': ['VGT', 'TNG', 'MSH', 'STK', 'GIL', 'TCM', 'TET', 'PHC'],
            'Food_Beverage': ['VNM', 'MSN', 'MCH', 'KDC', 'CII', 'VHC', 'QNS', 'SBT', 'ANV', 'DBC'],

            # Technology & Telecommunications
            'Technology': ['FPT', 'CMG', 'ELC', 'ITD', 'SAM', 'NTC', 'DSN', 'CMT', 'IFS'],
            'Telecommunications': ['VGI', 'MFS', 'EFI', 'YEG', 'CTR', 'VNZ'],

            # Energy & Utilities
            'Oil_Gas': ['GAS', 'PLX', 'PVS', 'PVD', 'PVC', 'BSR', 'PVG', 'CNG', 'PVB'],
            'Utilities': ['POW', 'SBA', 'PC1', 'VSH', 'NPS', 'SJF', 'BWE'],

            # Consumer & Retail
            'Retail': ['MWG', 'PNJ', 'DGW', 'FRT', 'AST', 'GMD', 'SFS', 'VRE'],
            'Airlines': ['HVN', 'VJC', 'ACV', 'SGN', 'VNA'],
            'Logistics': ['GMD', 'VSC', 'STG', 'TCO', 'ACS', 'TMS'],

            # Healthcare & Pharmaceuticals
            'Healthcare': ['DHG', 'IMP', 'TRA', 'PME', 'TNH', 'AMV', 'DBD', 'SPM'],

            # Agriculture & Aquaculture
            'Agriculture': ['BAF', 'HNG', 'VNH', 'FMC', 'LAF', 'ASM', 'SSC', 'ACL'],
            'Aquaculture': ['VHC', 'ANV', 'IDI', 'CMX', 'TS4', 'NAF']
        }

    def discover_all_stocks(self) -> List[str]:
        """Discover all available stocks from vnstock"""
        logging.info("Discovering all available Vietnamese stocks...")

        try:
            # Use vnstock's listing functionality to get all stocks
            listing = vn.Listing()

            all_stocks = []

            # Get stocks from major exchanges
            for exchange in ['HOSE', 'HNX']:
                try:
                    exchange_stocks = listing.symbols(exchange=exchange)
                    if exchange_stocks is not None:
                        if isinstance(exchange_stocks, pd.DataFrame):
                            symbols = exchange_stocks['symbol'].tolist()
                        else:
                            symbols = exchange_stocks
                        all_stocks.extend(symbols)
                        logging.info(f"Found {len(symbols)} stocks on {exchange}")
                except Exception as e:
                    logging.warning(f"Could not get stocks from {exchange}: {e}")

            # Remove duplicates and filter
            unique_stocks = list(set(all_stocks))
            logging.info(f"Total unique stocks discovered: {len(unique_stocks)}")

            return unique_stocks

        except Exception as e:
            logging.error(f"Error discovering stocks: {e}")
            # Fallback to known stock list
            return self.get_fallback_stock_list()

    def get_fallback_stock_list(self) -> List[str]:
        """Comprehensive fallback list of Vietnamese stocks"""
        all_known_stocks = []
        for sector_stocks in self.sector_mapping.values():
            all_known_stocks.extend(sector_stocks)

        # Add additional major stocks
        additional_stocks = [
            # Major HOSE stocks
            'VIC', 'VHM', 'VCB', 'BID', 'CTG', 'FPT', 'GAS', 'MSN', 'MWG', 'PLX',
            'POW', 'SAB', 'STB', 'TCB', 'TPB', 'VJC', 'VNM', 'VPB', 'VRE',

            # HNX leaders
            'SHB', 'ACB', 'CEO', 'HDB', 'KLB', 'NVB', 'PVS', 'TNG', 'VCS', 'VND',

            # High-volume stocks
            'HPG', 'HSG', 'SSI', 'VCI', 'MBB', 'EIB', 'LPB', 'OCB', 'VIB'
        ]

        all_known_stocks.extend(additional_stocks)
        return list(set(all_known_stocks))  # Remove duplicates

    def analyze_liquidity(self, symbol: str) -> Dict:
        """Analyze liquidity metrics for a stock"""
        try:
            # Get 1 year of data for liquidity analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'liquid': False, 'reason': 'No data available'}

            # Calculate liquidity metrics
            avg_price = data['close'].mean()
            avg_volume = data['volume'].mean()
            trading_days = len(data)

            # Estimate market cap (rough calculation)
            latest_price = data['close'].iloc[-1]
            # Assume ~50M shares outstanding (will be refined with actual data)
            estimated_shares = 50000000  # This would need actual shares outstanding data
            market_cap = latest_price * estimated_shares

            # Calculate volatility
            daily_returns = data['close'].pct_change().dropna()
            avg_volatility = daily_returns.std() if len(daily_returns) > 0 else 0

            # Check liquidity criteria
            liquidity_check = {
                'avg_price': avg_price,
                'avg_volume': avg_volume,
                'trading_days': trading_days,
                'market_cap': market_cap,
                'avg_volatility': avg_volatility,
                'price_ok': avg_price >= self.liquidity_filters['min_price'],
                'volume_ok': avg_volume >= self.liquidity_filters['min_avg_volume'],
                'trading_ok': trading_days >= self.liquidity_filters['min_trading_days'],
                'volatility_ok': avg_volatility <= self.liquidity_filters['max_daily_volatility']
            }

            # Determine if stock is liquid
            is_liquid = all([
                liquidity_check['price_ok'],
                liquidity_check['volume_ok'],
                liquidity_check['trading_ok'],
                liquidity_check['volatility_ok']
            ])

            return {
                'symbol': symbol,
                'liquid': is_liquid,
                'metrics': liquidity_check,
                'score': sum([
                    liquidity_check['price_ok'],
                    liquidity_check['volume_ok'],
                    liquidity_check['trading_ok'],
                    liquidity_check['volatility_ok']
                ]) / 4 * 100  # Percentage score
            }

        except Exception as e:
            logging.warning(f"Could not analyze liquidity for {symbol}: {e}")
            return {'symbol': symbol, 'liquid': False, 'reason': str(e)}

    def classify_stock_sector(self, symbol: str) -> str:
        """Classify stock into sector based on symbol"""
        for sector, stocks in self.sector_mapping.items():
            if symbol in stocks:
                return sector
        return 'Other'

    def build_liquid_stock_universe(self) -> Dict:
        """Build complete universe of liquid Vietnamese stocks"""
        logging.info("Building liquid stock universe...")

        # Discover all stocks
        all_stocks = self.discover_all_stocks()

        liquid_stocks = {}
        failed_stocks = []

        # Analyze liquidity for each stock (with rate limiting)
        for i, symbol in enumerate(all_stocks[:100]):  # Limit to first 100 for testing
            logging.info(f"Analyzing {symbol} ({i+1}/{min(100, len(all_stocks))})")

            liquidity_analysis = self.analyze_liquidity(symbol)

            if liquidity_analysis['liquid']:
                sector = self.classify_stock_sector(symbol)

                if sector not in liquid_stocks:
                    liquid_stocks[sector] = []

                liquid_stocks[sector].append({
                    'symbol': symbol,
                    'sector': sector,
                    'liquidity_score': liquidity_analysis['score'],
                    'avg_price': liquidity_analysis['metrics']['avg_price'],
                    'avg_volume': liquidity_analysis['metrics']['avg_volume'],
                    'trading_days': liquidity_analysis['metrics']['trading_days'],
                    'avg_volatility': liquidity_analysis['metrics']['avg_volatility']
                })
            else:
                failed_stocks.append({
                    'symbol': symbol,
                    'reason': liquidity_analysis.get('reason', 'Failed liquidity test')
                })

            # Rate limiting to avoid overwhelming the API
            time.sleep(1.5)

        # Sort by liquidity score within each sector
        for sector in liquid_stocks:
            liquid_stocks[sector].sort(key=lambda x: x['liquidity_score'], reverse=True)

        # Summary statistics
        total_liquid = sum(len(stocks) for stocks in liquid_stocks.values())

        logging.info(f"Liquid stock universe built: {total_liquid} stocks across {len(liquid_stocks)} sectors")

        return {
            'liquid_stocks': liquid_stocks,
            'failed_stocks': failed_stocks,
            'total_liquid': total_liquid,
            'total_analyzed': len(all_stocks[:100]),
            'filters_used': self.liquidity_filters,
            'created_at': datetime.now().isoformat()
        }

    def save_stock_universe(self, universe: Dict):
        """Save the stock universe to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/workspaces/BMAD-METHOD/session_logs/stock_universe_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(universe, f, indent=2, default=str)

        logging.info(f"Stock universe saved to {filename}")

        # Also create a CSV for easy viewing
        csv_data = []
        for sector, stocks in universe['liquid_stocks'].items():
            for stock in stocks:
                csv_data.append({
                    'Symbol': stock['symbol'],
                    'Sector': sector,
                    'Liquidity_Score': stock['liquidity_score'],
                    'Avg_Price': f"{stock['avg_price']:,.0f}",
                    'Avg_Volume': f"{stock['avg_volume']:,.0f}",
                    'Trading_Days': stock['trading_days'],
                    'Avg_Volatility': f"{stock['avg_volatility']:.2%}"
                })

        df = pd.DataFrame(csv_data)
        csv_filename = f'/workspages/BMAD-METHOD/session_logs/liquid_stocks_{timestamp}.csv'
        df.to_csv(csv_filename, index=False)

        return filename

    def get_top_stocks_by_sector(self, universe: Dict, top_n: int = 10) -> Dict:
        """Get top N most liquid stocks by sector"""
        top_stocks = {}

        for sector, stocks in universe['liquid_stocks'].items():
            top_stocks[sector] = stocks[:top_n]

        return top_stocks

if __name__ == "__main__":
    universe_manager = VietnamStockUniverse()

    # Build the liquid stock universe
    universe = universe_manager.build_liquid_stock_universe()

    # Save the universe
    filename = universe_manager.save_stock_universe(universe)

    # Print summary
    print(f"\n🏗️  VIETNAM LIQUID STOCK UNIVERSE BUILT")
    print("=" * 50)
    print(f"Total liquid stocks: {universe['total_liquid']}")
    print(f"Total analyzed: {universe['total_analyzed']}")
    print(f"Success rate: {universe['total_liquid']/universe['total_analyzed']*100:.1f}%")

    print(f"\n📊 STOCKS BY SECTOR:")
    for sector, stocks in universe['liquid_stocks'].items():
        print(f"{sector:20} | {len(stocks):3d} stocks")

    # Show top 5 stocks by liquidity score
    all_stocks = []
    for stocks in universe['liquid_stocks'].values():
        all_stocks.extend(stocks)

    top_stocks = sorted(all_stocks, key=lambda x: x['liquidity_score'], reverse=True)[:10]

    print(f"\n🚀 TOP 10 MOST LIQUID STOCKS:")
    for i, stock in enumerate(top_stocks, 1):
        print(f"{i:2d}. {stock['symbol']:4} | {stock['sector']:15} | Score: {stock['liquidity_score']:.1f}")

    print(f"\n💾 Data saved to: {filename}")
    print("✅ Ready to expand your tracking system!")