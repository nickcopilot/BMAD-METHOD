#!/usr/bin/env python3
"""
Daily Data Collector for Vietnam Stock Analysis System
Automated script to collect stock data and update Google Sheets
"""

import vnstock as vn
import pandas as pd
import json
import requests
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/workspaces/BMAD-METHOD/session_logs/data_collector.log'),
        logging.StreamHandler()
    ]
)

# Your priority stocks configuration
STOCK_CONFIG = {
    'Securities': {'stocks': ['SSI', 'VCI', 'VND', 'HCM'], 'weight': 1.0},
    'Banks': {'stocks': ['VCB', 'BID', 'CTG', 'TCB', 'MBB'], 'weight': 1.2},
    'Real_Estate': {'stocks': ['VHM', 'VIC', 'NVL', 'DXG'], 'weight': 0.9},
    'Steel': {'stocks': ['HPG', 'HSG', 'NKG', 'TLH'], 'weight': 1.1}
}

class VietnamStockCollector:
    def __init__(self):
        self.session_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.data_cache = {}
        self.economic_data = {}

    def get_stock_data(self, symbol, source='VCI'):
        """Collect data for a single stock"""
        try:
            logging.info(f"Collecting data for {symbol}")

            # Initialize stock object
            stock = vn.Vnstock().stock(symbol=symbol, source=source)

            # Get price history (last 30 days)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

            price_data = stock.quote.history(start=start_date, end=end_date, interval='1D')

            if price_data is not None and not price_data.empty:
                latest = price_data.iloc[-1]
                previous = price_data.iloc[-2] if len(price_data) > 1 else latest

                # Calculate metrics
                change_pct = ((latest['close'] - previous['close']) / previous['close'] * 100) if len(price_data) > 1 else 0
                avg_volume = price_data['volume'].mean()
                volume_ratio = latest['volume'] / avg_volume if avg_volume > 0 else 1

                # Try to get company info
                try:
                    company_info = stock.company.overview()
                    company_name = company_info.get('companyName', symbol) if company_info else symbol
                except:
                    company_name = symbol

                return {
                    'symbol': symbol,
                    'company_name': company_name,
                    'current_price': float(latest['close']),
                    'previous_close': float(previous['close']),
                    'change_pct': float(change_pct),
                    'volume': int(latest['volume']),
                    'high': float(latest['high']),
                    'low': float(latest['low']),
                    'avg_volume_30d': float(avg_volume),
                    'volume_ratio': float(volume_ratio),
                    'price_data_points': len(price_data),
                    'success': True,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {'symbol': symbol, 'success': False, 'error': 'No price data'}

        except Exception as e:
            logging.error(f"Error collecting {symbol}: {str(e)}")
            return {'symbol': symbol, 'success': False, 'error': str(e)}

    def calculate_eic_score(self, stock_data, sector):
        """Calculate EIC score for a stock"""
        if not stock_data.get('success', False):
            return {'total_score': 1.0, 'economy': 1.0, 'industry': 1.0, 'company': 1.0}

        # Economy Score (30%) - Based on macro factors
        economy_score = self.get_economy_score()

        # Industry Score (40%) - Based on sector performance and stock momentum
        industry_score = self.get_industry_score(stock_data, sector)

        # Company Score (30%) - Based on financial health indicators
        company_score = self.get_company_score(stock_data)

        # Weighted total score
        total_score = (economy_score * 0.3) + (industry_score * 0.4) + (company_score * 0.3)

        return {
            'total_score': round(total_score, 1),
            'economy': round(economy_score, 1),
            'industry': round(industry_score, 1),
            'company': round(company_score, 1)
        }

    def get_economy_score(self):
        """Calculate economy-level score (simplified)"""
        # In real implementation, this would pull from GSO.gov.vn
        # For now, using reasonable Vietnam macro assumptions
        base_score = 5.0

        # Positive factors for Vietnam economy
        gdp_growth_factor = 1.0  # 6.5%+ GDP growth
        inflation_factor = 0.5   # Low inflation ~2.5%
        currency_factor = 0.0    # Stable VND

        return min(10.0, max(1.0, base_score + gdp_growth_factor + inflation_factor + currency_factor))

    def get_industry_score(self, stock_data, sector):
        """Calculate industry-level score"""
        base_score = 5.0

        # Sector-specific adjustments
        sector_weights = STOCK_CONFIG.get(sector, {}).get('weight', 1.0)
        sector_adjustment = (sector_weights - 1.0) * 2  # Convert to score adjustment

        # Price momentum factor
        momentum_score = 0
        if stock_data['change_pct'] > 3:
            momentum_score = 2.0
        elif stock_data['change_pct'] > 1:
            momentum_score = 1.0
        elif stock_data['change_pct'] > 0:
            momentum_score = 0.5
        elif stock_data['change_pct'] < -3:
            momentum_score = -2.0
        elif stock_data['change_pct'] < -1:
            momentum_score = -1.0

        # Volume factor
        volume_score = 0
        if stock_data['volume_ratio'] > 2:
            volume_score = 1.0
        elif stock_data['volume_ratio'] > 1.5:
            volume_score = 0.5

        total = base_score + sector_adjustment + momentum_score + volume_score
        return min(10.0, max(1.0, total))

    def get_company_score(self, stock_data):
        """Calculate company-level score (simplified)"""
        # In real implementation, would use financial ratios from vnstock
        base_score = 5.0

        # Price stability factor
        stability_score = 0
        if abs(stock_data['change_pct']) < 1:
            stability_score = 0.5
        elif abs(stock_data['change_pct']) > 5:
            stability_score = -0.5

        # Volume consistency
        volume_score = 0
        if 0.5 <= stock_data['volume_ratio'] <= 2.0:
            volume_score = 0.5

        total = base_score + stability_score + volume_score
        return min(10.0, max(1.0, total))

    def generate_signal(self, eic_score):
        """Generate buy/sell signal based on EIC score"""
        if eic_score >= 7.5:
            return 'STRONG_BUY'
        elif eic_score >= 6.5:
            return 'BUY'
        elif eic_score >= 4.5:
            return 'HOLD'
        elif eic_score >= 3.0:
            return 'SELL'
        else:
            return 'STRONG_SELL'

    def collect_all_stocks(self):
        """Collect data for all priority stocks"""
        logging.info("Starting daily stock data collection")

        all_data = []
        sector_summaries = {}

        for sector, config in STOCK_CONFIG.items():
            logging.info(f"Processing {sector} sector")
            sector_data = []

            for symbol in config['stocks']:
                # Get stock data
                stock_data = self.get_stock_data(symbol)

                if stock_data.get('success'):
                    # Calculate EIC scores
                    eic_scores = self.calculate_eic_score(stock_data, sector)

                    # Generate signal
                    signal = self.generate_signal(eic_scores['total_score'])

                    # Combine all data
                    combined_data = {
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'symbol': symbol,
                        'company_name': stock_data['company_name'],
                        'sector': sector,
                        'current_price': stock_data['current_price'],
                        'previous_close': stock_data['previous_close'],
                        'change_pct': stock_data['change_pct'],
                        'volume': stock_data['volume'],
                        'high': stock_data['high'],
                        'low': stock_data['low'],
                        'eic_score': eic_scores['total_score'],
                        'economy_score': eic_scores['economy'],
                        'industry_score': eic_scores['industry'],
                        'company_score': eic_scores['company'],
                        'signal': signal,
                        'last_updated': datetime.now().isoformat()
                    }

                    all_data.append(combined_data)
                    sector_data.append(combined_data)

                    logging.info(f"✅ {symbol}: {stock_data['current_price']:,.0f} VND ({stock_data['change_pct']:+.2f}%) EIC: {eic_scores['total_score']}")
                else:
                    logging.error(f"❌ {symbol}: {stock_data.get('error', 'Unknown error')}")

                # Rate limiting
                time.sleep(1)

            # Calculate sector summary
            if sector_data:
                sector_summaries[sector] = {
                    'avg_change_pct': sum(s['change_pct'] for s in sector_data) / len(sector_data),
                    'avg_eic_score': sum(s['eic_score'] for s in sector_data) / len(sector_data),
                    'stocks_count': len(sector_data),
                    'top_performer': max(sector_data, key=lambda x: x['change_pct'])['symbol'],
                    'best_eic': max(sector_data, key=lambda x: x['eic_score'])['symbol']
                }

        # Save data
        self.save_daily_data(all_data)
        self.save_sector_summary(sector_summaries)

        logging.info(f"Data collection completed. {len(all_data)} stocks processed.")
        return all_data, sector_summaries

    def save_daily_data(self, data):
        """Save daily data to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Save as JSON
        json_file = f'/workspaces/BMAD-METHOD/session_logs/daily_stock_data_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

        # Save as CSV for Google Sheets
        df = pd.DataFrame(data)
        csv_file = f'/workspaces/BMAD-METHOD/session_logs/daily_stock_data_{timestamp}.csv'
        df.to_csv(csv_file, index=False)

        logging.info(f"Daily data saved to {json_file} and {csv_file}")

    def save_sector_summary(self, summaries):
        """Save sector analysis summary"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        summary_data = []
        for sector, data in summaries.items():
            summary_data.append({
                'date': datetime.now().strftime('%Y-%m-%d'),
                'sector': sector,
                'avg_change_pct': round(data['avg_change_pct'], 2),
                'avg_eic_score': round(data['avg_eic_score'], 1),
                'stocks_count': data['stocks_count'],
                'top_performer': data['top_performer'],
                'best_eic': data['best_eic'],
                'last_updated': datetime.now().isoformat()
            })

        # Save sector summary
        json_file = f'/workspaces/BMAD-METHOD/session_logs/sector_summary_{timestamp}.json'
        with open(json_file, 'w') as f:
            json.dump(summary_data, f, indent=2, default=str)

        csv_file = f'/workspaces/BMAD-METHOD/session_logs/sector_summary_{timestamp}.csv'
        pd.DataFrame(summary_data).to_csv(csv_file, index=False)

        logging.info(f"Sector summary saved to {json_file}")

    def check_portfolio_alerts(self, current_data):
        """Check for portfolio alerts (placeholder)"""
        # This would check your actual portfolio against current prices
        # and generate alerts for significant changes
        alerts = []

        # Example alert logic
        for stock in current_data:
            if stock['change_pct'] < -5:
                alerts.append({
                    'type': 'PRICE_DROP',
                    'symbol': stock['symbol'],
                    'message': f"{stock['symbol']} dropped {stock['change_pct']:.2f}%",
                    'severity': 'HIGH',
                    'timestamp': datetime.now().isoformat()
                })
            elif stock['change_pct'] > 5:
                alerts.append({
                    'type': 'PRICE_SURGE',
                    'symbol': stock['symbol'],
                    'message': f"{stock['symbol']} gained {stock['change_pct']:.2f}%",
                    'severity': 'MEDIUM',
                    'timestamp': datetime.now().isoformat()
                })

        if alerts:
            self.save_alerts(alerts)

        return alerts

    def save_alerts(self, alerts):
        """Save alerts to file"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alerts_file = f'/workspaces/BMAD-METHOD/session_logs/alerts_{timestamp}.json'

        with open(alerts_file, 'w') as f:
            json.dump(alerts, f, indent=2, default=str)

        logging.info(f"Saved {len(alerts)} alerts to {alerts_file}")

    def run_daily_collection(self):
        """Main method to run daily data collection"""
        logging.info("="*60)
        logging.info("VIETNAM STOCK ANALYSIS - DAILY DATA COLLECTION")
        logging.info("="*60)

        try:
            # Collect all stock data
            stock_data, sector_data = self.collect_all_stocks()

            # Check for alerts
            alerts = self.check_portfolio_alerts(stock_data)

            # Generate summary report
            self.generate_daily_report(stock_data, sector_data, alerts)

            logging.info("Daily collection completed successfully!")
            return True

        except Exception as e:
            logging.error(f"Daily collection failed: {str(e)}")
            return False

    def generate_daily_report(self, stock_data, sector_data, alerts):
        """Generate daily summary report"""
        report = f"""
# Daily Vietnam Stock Analysis Report - {datetime.now().strftime('%Y-%m-%d')}

## Market Summary
- Stocks Analyzed: {len(stock_data)}
- Alerts Generated: {len(alerts)}

## Sector Performance
"""
        for sector, data in sector_data.items():
            report += f"- **{sector}**: {data['avg_change_pct']:+.2f}% (EIC: {data['avg_eic_score']:.1f})\n"

        if stock_data:
            top_performer = max(stock_data, key=lambda x: x['change_pct'])
            worst_performer = min(stock_data, key=lambda x: x['change_pct'])

            report += f"""
## Top Performers
- **Best**: {top_performer['symbol']} ({top_performer['change_pct']:+.2f}%)
- **Worst**: {worst_performer['symbol']} ({worst_performer['change_pct']:+.2f}%)

## High EIC Scores
"""
            best_eic = sorted(stock_data, key=lambda x: x['eic_score'], reverse=True)[:3]
            for stock in best_eic:
                report += f"- **{stock['symbol']}**: EIC {stock['eic_score']} ({stock['signal']})\n"

        if alerts:
            report += f"\n## Alerts\n"
            for alert in alerts:
                report += f"- {alert['type']}: {alert['message']}\n"

        # Save report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f'/workspaces/BMAD-METHOD/session_logs/daily_report_{timestamp}.md'

        with open(report_file, 'w') as f:
            f.write(report)

        logging.info(f"Daily report saved to {report_file}")

if __name__ == "__main__":
    collector = VietnamStockCollector()
    collector.run_daily_collection()