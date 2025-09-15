#!/usr/bin/env python3
"""
Vietnam Stock Analysis - vnstock Library Test v2
Updated to use correct vnstock v3.x API
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

def test_vnstock_api():
    """Test vnstock v3.x API structure"""
    print("🔍 Exploring vnstock v3.x API...")

    try:
        # Test Quote class for stock data
        quote = vn.Quote()
        print("✅ Quote class initialized")

        # Test with VCB
        print("Testing Quote.history() with VCB...")
        data = quote.history(symbol='VCB', start='2024-09-01', end='2024-09-15')

        if data is not None and not data.empty:
            print(f"✅ Got {len(data)} rows of data for VCB")
            print(f"Latest close: {data['close'].iloc[-1]:,.0f} VND")
            return True, quote
        else:
            print("❌ No data returned")
            return False, None

    except Exception as e:
        print(f"❌ Error with Quote.history(): {e}")

        # Try alternative methods
        try:
            print("Trying alternative vnstock methods...")
            stock = vn.Vnstock()
            print("✅ Vnstock class initialized")
            return True, stock
        except Exception as e2:
            print(f"❌ Error with Vnstock(): {e2}")
            return False, None

def get_stock_data_v3(symbol, quote_obj):
    """Get stock data using vnstock v3 API"""
    try:
        # Get recent data (last 30 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        data = quote_obj.history(symbol=symbol, start=start_date, end=end_date)

        if data is not None and not data.empty:
            latest = data.iloc[-1]
            previous = data.iloc[-2] if len(data) > 1 else latest

            change_pct = ((latest['close'] - previous['close']) / previous['close'] * 100) if len(data) > 1 else 0

            return {
                'symbol': symbol,
                'current_price': latest['close'],
                'previous_close': previous['close'],
                'change_pct': change_pct,
                'volume': latest['volume'],
                'high': latest['high'],
                'low': latest['low'],
                'date': latest.name.strftime('%Y-%m-%d') if hasattr(latest.name, 'strftime') else str(latest.name),
                'success': True
            }
        else:
            return {'symbol': symbol, 'success': False, 'error': 'No data available'}

    except Exception as e:
        return {'symbol': symbol, 'success': False, 'error': str(e)}

def test_company_info():
    """Test company information retrieval"""
    try:
        print("🏢 Testing company information...")
        company = vn.Company()

        # Test with VCB
        info = company.profile(symbol='VCB')
        if info is not None:
            print("✅ Company profile data available")
            return True, company
        else:
            print("❌ No company profile data")
            return False, None
    except Exception as e:
        print(f"❌ Error getting company info: {e}")
        return False, None

def run_comprehensive_test():
    """Run comprehensive test of vnstock capabilities"""
    print("="*60)
    print("🏗️  VIETNAM STOCK ANALYSIS SYSTEM - COMPREHENSIVE TEST")
    print("="*60)

    # Test basic API
    api_success, quote_obj = test_vnstock_api()

    if not api_success:
        print("❌ Cannot proceed without working API")
        return

    # Test company info
    company_success, company_obj = test_company_info()

    # Test priority stocks
    print(f"\n📊 Testing priority stocks...")
    results = {}

    for sector, stocks in PRIORITY_STOCKS.items():
        print(f"\n🏢 {sector} Sector:")
        sector_results = []

        for stock in stocks[:3]:  # Test first 3 stocks per sector to avoid rate limits
            print(f"  📈 {stock}...", end=" ")

            if quote_obj:
                data = get_stock_data_v3(stock, quote_obj)

                if data['success']:
                    sector_results.append(data)
                    print(f"✅ {data['current_price']:,.0f} VND ({data['change_pct']:+.2f}%)")
                else:
                    print(f"❌ {data['error']}")
            else:
                print("❌ No quote object")

        results[sector] = sector_results

    # Generate summary
    print(f"\n📋 SUMMARY:")
    print("-" * 40)

    total_tested = 0
    total_success = 0

    for sector, stocks in results.items():
        success_count = len([s for s in stocks if s.get('success')])
        total_tested += len(PRIORITY_STOCKS[sector][:3])
        total_success += success_count

        if stocks:
            avg_change = sum(s['change_pct'] for s in stocks if s.get('success', False)) / max(1, success_count)
            print(f"{sector:15} | {success_count}/3 success | Avg: {avg_change:+6.2f}%")
        else:
            print(f"{sector:15} | 0/3 success")

    print(f"\nOverall Success Rate: {total_success}/{total_tested} ({total_success/max(1,total_tested)*100:.1f}%)")

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'/workspaces/BMAD-METHOD/session_logs/vnstock_test_v3_{timestamp}.json'

    with open(filename, 'w') as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Results saved to: {filename}")

    if total_success > 0:
        print("✅ vnstock integration successful! Ready to build your system.")
    else:
        print("❌ vnstock integration failed. Need alternative data source.")

    return results

if __name__ == "__main__":
    run_comprehensive_test()