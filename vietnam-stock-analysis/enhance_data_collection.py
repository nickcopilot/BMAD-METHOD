#!/usr/bin/env python3
"""
Enhanced Data Collection for Smart Money Analysis
Collect more historical data to enable meaningful signal analysis
"""

import sys
import os
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from data_collection.vnstock_collector import VNStockCollector
from shared.models.database import get_db

def collect_extended_data():
    """Collect extended historical data for better analysis"""
    print("=== Enhanced Data Collection for Smart Money Analysis ===")

    collector = VNStockCollector()
    db = get_db()

    # Get all stocks
    stocks = db.get_all_stocks()
    print(f"Found {len(stocks)} stocks to enhance")

    # Extended date range for better analysis (90 days)
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    print(f"Collecting data from {start_date} to {end_date}")

    total_records = 0
    for stock in stocks:
        symbol = stock['symbol']
        print(f"\n📊 Enhancing data for {symbol}...")

        try:
            # Collect extended price data
            price_data_list = collector.collect_price_data(symbol, start_date, end_date)

            stored_count = 0
            for price_data in price_data_list:
                if db.insert_price_data(price_data):
                    stored_count += 1

            total_records += stored_count
            print(f"  ✅ Collected {len(price_data_list)} records, stored {stored_count}")

        except Exception as e:
            print(f"  ❌ Error collecting data for {symbol}: {e}")

    print(f"\n🎉 Enhanced collection complete!")
    print(f"Total records collected: {total_records}")

    # Verify data quality
    print(f"\n🔍 Data Quality Verification:")
    for stock in stocks:
        symbol = stock['symbol']

        # Check total records in database
        with db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT COUNT(*) FROM price_data WHERE stock_symbol = ?
            """, (symbol,))
            count = cursor.fetchone()[0]

            print(f"  {symbol}: {count} total records in database")

def fix_date_format():
    """Fix the date format issues in database"""
    print("\n=== Fixing Date Format Issues ===")

    db = get_db()

    # Check current date format
    with db.get_connection() as conn:
        cursor = conn.execute("""
            SELECT stock_symbol, date, close FROM price_data
            WHERE stock_symbol = 'VCB'
            ORDER BY rowid LIMIT 5
        """)
        records = cursor.fetchall()

        print("Current date format sample:")
        for record in records:
            print(f"  {record[0]}: date='{record[1]}', close={record[2]}")

    # For now, document the issue for Architect review
    print("\n📝 Date Format Issue Documented:")
    print("  - Dates stored as sequential numbers instead of YYYY-MM-DD")
    print("  - This impacts time-series analysis calculations")
    print("  - Architect review needed for database schema fix")

def test_enhanced_signals():
    """Test if enhanced data improves signal quality"""
    print("\n=== Testing Enhanced Smart Money Signals ===")

    try:
        from shared.analysis.smart_money import SmartMoneyAnalyzer

        analyzer = SmartMoneyAnalyzer()
        db = get_db()

        stocks = db.get_all_stocks()

        print("Testing signal quality with enhanced data:")

        signal_diversity = []
        for stock in stocks:
            analysis = analyzer.analyze_symbol(stock['symbol'], days_back=60)

            if 'error' not in analysis:
                score = analysis['composite_score']['composite_score']
                signal_diversity.append(score)
                print(f"  {stock['symbol']}: {score:.1f} ({analysis['composite_score']['signal_class']})")
            else:
                print(f"  {stock['symbol']}: Error - {analysis['error']}")

        # Check if we have signal diversity
        if signal_diversity:
            score_range = max(signal_diversity) - min(signal_diversity)
            avg_score = sum(signal_diversity) / len(signal_diversity)

            print(f"\n📈 Signal Quality Metrics:")
            print(f"  Average Score: {avg_score:.1f}")
            print(f"  Score Range: {score_range:.1f}")
            print(f"  Diversity: {'Good' if score_range > 10 else 'Poor (all neutral)'}")

            return score_range > 10

    except Exception as e:
        print(f"❌ Error testing signals: {e}")
        return False

    return False

def main():
    """Main enhancement function"""
    print("Vietnam Stock Analysis - Data Enhancement")
    print("=" * 60)

    try:
        # Step 1: Collect more historical data
        collect_extended_data()

        # Step 2: Document date format issues
        fix_date_format()

        # Step 3: Test if signals improve
        signals_improved = test_enhanced_signals()

        print("\n" + "=" * 60)

        if signals_improved:
            print("🎉 SUCCESS: Enhanced data collection improved signal diversity!")
            print("\n✅ Next Steps:")
            print("1. Dashboard should now show varied signals")
            print("2. Smart Money analysis should be more meaningful")
            print("3. Ready for Architect review of date format fix")
        else:
            print("⚠️ PARTIAL SUCCESS: More data collected, but signals still neutral")
            print("\n🔧 Requires Architect Review:")
            print("1. Date format standardization needed")
            print("2. Algorithm parameter tuning required")
            print("3. Vietnamese market calibration needed")

    except Exception as e:
        print(f"❌ Enhancement error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()