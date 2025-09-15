#!/usr/bin/env python3
"""
Vietnam Stock Analysis - Working vnstock Implementation
Using correct vnstock v3.x API
"""

import vnstock as vn
import pandas as pd
from datetime import datetime, timedelta
import json
import time

# Your priority stocks by sector
PRIORITY_STOCKS = {
    'Securities': ['SSI', 'VCI', 'VND', 'HCM'],
    'Banks': ['VCB', 'BID', 'CTG', 'TCB', 'MBB'],
    'Real_Estate': ['VHM', 'VIC', 'NVL', 'DXG'],
    'Steel': ['HPG', 'HSG', 'NKG', 'TLH']
}

def get_stock_data(symbol, source='VCI'):
    """Get stock data using correct vnstock v3 API"""
    try:
        print(f"  📈 Getting data for {symbol}...", end=" ")

        # Initialize stock object
        stock = vn.Vnstock().stock(symbol=symbol, source=source)

        # Get recent price history
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        price_data = stock.quote.history(start=start_date, end=end_date, interval='1D')

        if price_data is not None and not price_data.empty:
            latest = price_data.iloc[-1]
            previous = price_data.iloc[-2] if len(price_data) > 1 else latest

            # Calculate change percentage
            change_pct = ((latest['close'] - previous['close']) / previous['close'] * 100) if len(price_data) > 1 else 0

            # Try to get company overview
            try:
                company_info = stock.company.overview()
                company_name = company_info.get('companyName', symbol) if company_info is not None else symbol
            except:
                company_name = symbol

            result = {
                'symbol': symbol,
                'company_name': company_name,
                'current_price': float(latest['close']),
                'previous_close': float(previous['close']),
                'change_pct': float(change_pct),
                'volume': int(latest['volume']) if 'volume' in latest else 0,
                'high': float(latest['high']),
                'low': float(latest['low']),
                'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
                'data_points': len(price_data),
                'success': True
            }

            print(f"✅ {result['current_price']:,.0f} VND ({result['change_pct']:+.2f}%)")
            return result

        else:
            print("❌ No price data")
            return {'symbol': symbol, 'success': False, 'error': 'No price data available'}

    except Exception as e:
        print(f"❌ Error: {str(e)[:50]}...")
        return {'symbol': symbol, 'success': False, 'error': str(e)}

def calculate_basic_eic_score(stock_data):
    """Calculate basic EIC score for testing"""
    if not stock_data.get('success', False):
        return 1.0

    score = 5.0  # Base score

    # Economy factors (simplified - normally would use macro data)
    # Using market-wide momentum as proxy
    economy_score = 5.0  # Neutral for now

    # Industry factors (sector momentum)
    # Price momentum component
    if stock_data['change_pct'] > 5:
        industry_score = 8.0
    elif stock_data['change_pct'] > 2:
        industry_score = 7.0
    elif stock_data['change_pct'] > 0:
        industry_score = 6.0
    elif stock_data['change_pct'] > -2:
        industry_score = 4.0
    else:
        industry_score = 3.0

    # Company factors (financial health - simplified)
    company_score = 5.0  # Would normally use financial ratios

    # Weighted EIC score
    eic_score = (economy_score * 0.3) + (industry_score * 0.4) + (company_score * 0.3)

    return round(eic_score, 1)

def test_working_vnstock():
    """Test vnstock with working API"""
    print("="*60)
    print("🏗️  VIETNAM STOCK ANALYSIS - WORKING TEST")
    print("="*60)

    results = {}
    all_stocks = []

    for sector, stocks in PRIORITY_STOCKS.items():
        print(f"\n🏢 {sector} Sector:")
        sector_results = []

        # Test first 2 stocks per sector to avoid rate limits
        for stock in stocks[:2]:
            data = get_stock_data(stock)

            if data.get('success'):
                # Add EIC score
                data['eic_score'] = calculate_basic_eic_score(data)
                sector_results.append(data)
                all_stocks.append(data)

            # Small delay to avoid rate limiting
            time.sleep(1)

        results[sector] = sector_results

    # Generate analysis
    print(f"\n📊 ANALYSIS RESULTS:")
    print("-" * 50)

    total_success = sum(len(stocks) for stocks in results.values())
    print(f"Successfully analyzed: {total_success} stocks")

    if all_stocks:
        # Top performers
        top_performers = sorted(all_stocks, key=lambda x: x['change_pct'], reverse=True)

        print(f"\n🚀 TOP PERFORMERS:")
        for i, stock in enumerate(top_performers[:5], 1):
            print(f"{i}. {stock['symbol']:4} | {stock['current_price']:8,.0f} VND | {stock['change_pct']:+6.2f}% | EIC: {stock['eic_score']}")

        # Best EIC scores
        best_eic = sorted(all_stocks, key=lambda x: x['eic_score'], reverse=True)

        print(f"\n⭐ BEST EIC SCORES:")
        for i, stock in enumerate(best_eic[:5], 1):
            signal = "🟢 BUY" if stock['eic_score'] >= 7 else "🟡 HOLD" if stock['eic_score'] >= 5 else "🔴 SELL"
            print(f"{i}. {stock['symbol']:4} | EIC: {stock['eic_score']} | {signal}")

        # Sector performance
        print(f"\n🏭 SECTOR PERFORMANCE:")
        for sector, stocks in results.items():
            if stocks:
                avg_change = sum(s['change_pct'] for s in stocks) / len(stocks)
                avg_eic = sum(s['eic_score'] for s in stocks) / len(stocks)
                print(f"{sector:15} | Avg Change: {avg_change:+6.2f}% | Avg EIC: {avg_eic:.1f}")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'/workspaces/BMAD-METHOD/session_logs/vnstock_working_{timestamp}.json'

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Results saved to: {filename}")

    if total_success > 0:
        print(f"✅ SUCCESS! vnstock integration working with {total_success} stocks")
        print("🚀 Ready to build your full system!")

        # Create sample portfolio for testing
        create_sample_portfolio(all_stocks[:3])
    else:
        print("❌ No stocks successfully analyzed")

    return results

def create_sample_portfolio(stocks):
    """Create a sample portfolio for testing alerts"""
    print(f"\n📁 CREATING SAMPLE PORTFOLIO:")
    print("-" * 30)

    portfolio = []
    for stock in stocks:
        position = {
            'symbol': stock['symbol'],
            'quantity': 100,  # Sample quantity
            'avg_price': stock['current_price'] * 0.95,  # Assume bought 5% lower
            'current_price': stock['current_price'],
            'market_value': stock['current_price'] * 100,
            'unrealized_pnl': (stock['current_price'] - (stock['current_price'] * 0.95)) * 100,
            'unrealized_pnl_pct': 5.26,  # 5% gain
            'eic_score': stock['eic_score'],
            'alert_triggers': {
                'price_drop_5pct': stock['current_price'] * 0.95,
                'eic_score_change': 1.0,
                'volume_spike': 2.0
            }
        }
        portfolio.append(position)

        pnl_color = "🟢" if position['unrealized_pnl'] > 0 else "🔴"
        print(f"{stock['symbol']:4} | {position['quantity']:3d} shares | {pnl_color} {position['unrealized_pnl_pct']:+.1f}%")

    # Save sample portfolio
    portfolio_file = '/workspaces/BMAD-METHOD/session_logs/sample_portfolio.json'
    with open(portfolio_file, 'w') as f:
        json.dump(portfolio, f, indent=2, default=str)

    print(f"📊 Portfolio saved to: {portfolio_file}")

    return portfolio

if __name__ == "__main__":
    test_working_vnstock()