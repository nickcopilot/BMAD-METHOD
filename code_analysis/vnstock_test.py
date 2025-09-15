#!/usr/bin/env python3
"""
Vietnam Stock Analysis - vnstock Library Test
Testing data collection for priority sectors: Securities, Banks, Real Estate, Steel
"""

import vnstock as vn
import pandas as pd
from datetime import datetime, timedelta
import json

# Your priority stocks by sector
PRIORITY_STOCKS = {
    'Securities': ['SSI', 'VCI', 'VND', 'HCM'],
    'Banks': ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'TPB'],
    'Real_Estate': ['VHM', 'VIC', 'NVL', 'DXG', 'KDH', 'HDG'],
    'Steel': ['HPG', 'HSG', 'NKG', 'TLH', 'SMC']
}

def test_vnstock_basic():
    """Test basic vnstock functionality"""
    print("🔍 Testing vnstock basic functionality...")

    try:
        # Test with a major stock - VCB (Vietcombank)
        print("Testing with VCB (Vietcombank)...")

        # Get current price
        current_data = vn.stock_historical_data(
            symbol='VCB',
            start_date='2024-09-01',
            end_date='2024-09-15',
            source='VCI'
        )

        if not current_data.empty:
            latest_price = current_data['close'].iloc[-1]
            latest_volume = current_data['volume'].iloc[-1]
            print(f"✅ VCB Latest Price: {latest_price:,.0f} VND")
            print(f"✅ VCB Latest Volume: {latest_volume:,.0f}")
            return True
        else:
            print("❌ No data returned for VCB")
            return False

    except Exception as e:
        print(f"❌ Error testing vnstock: {e}")
        return False

def get_stock_data(symbol, days=30):
    """Get stock data for a specific symbol"""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = vn.stock_historical_data(
            symbol=symbol,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d'),
            source='VCI'
        )

        if not data.empty:
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else latest

            change_pct = ((latest['close'] - previous['close']) / previous['close'] * 100)

            return {
                'symbol': symbol,
                'current_price': latest['close'],
                'previous_close': previous['close'],
                'change_pct': change_pct,
                'volume': latest['volume'],
                'high_52w': data['high'].max(),
                'low_52w': data['low'].min(),
                'avg_volume_30d': data['volume'].mean(),
                'last_updated': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name)
            }
    except Exception as e:
        print(f"❌ Error getting data for {symbol}: {e}")
        return None

def test_all_priority_stocks():
    """Test data collection for all priority stocks"""
    print("\n📊 Testing all priority stocks...")

    results = {}

    for sector, stocks in PRIORITY_STOCKS.items():
        print(f"\n🏢 Testing {sector} sector...")
        sector_data = []

        for stock in stocks:
            print(f"  📈 Getting data for {stock}...")
            data = get_stock_data(stock)

            if data:
                sector_data.append(data)
                print(f"    ✅ {stock}: {data['current_price']:,.0f} VND ({data['change_pct']:+.2f}%)")
            else:
                print(f"    ❌ {stock}: Failed to get data")

        results[sector] = sector_data

    return results

def calculate_basic_eic_score(stock_data):
    """Calculate a basic EIC score for testing"""
    if not stock_data:
        return 0

    # Simple scoring based on price momentum and volume
    score = 5.0  # Base score

    # Price momentum (30% of score)
    if stock_data['change_pct'] > 5:
        score += 1.5
    elif stock_data['change_pct'] > 2:
        score += 1.0
    elif stock_data['change_pct'] > 0:
        score += 0.5
    elif stock_data['change_pct'] < -5:
        score -= 1.5
    elif stock_data['change_pct'] < -2:
        score -= 1.0

    # Volume analysis (20% of score)
    volume_ratio = stock_data['volume'] / stock_data['avg_volume_30d']
    if volume_ratio > 2:
        score += 1.0
    elif volume_ratio > 1.5:
        score += 0.5

    # Position in 52-week range (20% of score)
    current_price = stock_data['current_price']
    price_range = stock_data['high_52w'] - stock_data['low_52w']
    position_in_range = (current_price - stock_data['low_52w']) / price_range

    if position_in_range > 0.8:
        score += 1.0
    elif position_in_range > 0.6:
        score += 0.5
    elif position_in_range < 0.3:
        score -= 0.5

    return max(1.0, min(10.0, score))

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n" + "="*60)
    print("🏗️  VIETNAM STOCK ANALYSIS SYSTEM - TEST REPORT")
    print("="*60)

    # Test basic functionality
    basic_test = test_vnstock_basic()

    if not basic_test:
        print("❌ Basic test failed. Cannot proceed.")
        return

    # Test all priority stocks
    all_data = test_all_priority_stocks()

    # Generate summary
    print("\n📋 SECTOR SUMMARY:")
    print("-" * 40)

    for sector, stocks in all_data.items():
        if stocks:
            avg_change = sum(s['change_pct'] for s in stocks) / len(stocks)
            print(f"{sector:15} | {len(stocks):2d} stocks | Avg Change: {avg_change:+6.2f}%")
        else:
            print(f"{sector:15} | No data available")

    # Find top performers
    print("\n🚀 TOP PERFORMERS TODAY:")
    print("-" * 40)

    all_stocks_flat = []
    for stocks in all_data.values():
        all_stocks_flat.extend(stocks)

    if all_stocks_flat:
        top_performers = sorted(all_stocks_flat, key=lambda x: x['change_pct'], reverse=True)[:5]

        for i, stock in enumerate(top_performers, 1):
            eic_score = calculate_basic_eic_score(stock)
            print(f"{i}. {stock['symbol']:4} | {stock['current_price']:8,.0f} VND | {stock['change_pct']:+6.2f}% | EIC: {eic_score:.1f}")

    # Save detailed results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'/workspaces/BMAD-METHOD/session_logs/vnstock_test_{timestamp}.json'

    with open(filename, 'w') as f:
        json.dump(all_data, f, indent=2)

    print(f"\n💾 Detailed results saved to: {filename}")
    print(f"✅ Test completed successfully!")

    return all_data

if __name__ == "__main__":
    generate_test_report()