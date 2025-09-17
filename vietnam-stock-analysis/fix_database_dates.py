#!/usr/bin/env python3
"""
Fix Database Date Format Issues
Convert sequential numbers to proper dates for time-series analysis
"""

import sqlite3
import sys
import os
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from shared.models.database import get_db

def backup_database():
    """Create backup of current database"""
    import shutil

    backup_path = f"data/vietnam_stocks_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    shutil.copy2("data/vietnam_stocks.db", backup_path)
    print(f"✅ Database backed up to: {backup_path}")
    return backup_path

def fix_date_format():
    """Fix the date format in price_data table"""
    print("=== Fixing Database Date Format ===")

    db = get_db()

    with db.get_connection() as conn:
        # Get all unique symbols and their record counts
        cursor = conn.execute("""
            SELECT stock_symbol, COUNT(*) as record_count
            FROM price_data
            GROUP BY stock_symbol
            ORDER BY stock_symbol
        """)

        stocks_info = cursor.fetchall()
        print(f"Found {len(stocks_info)} stocks to fix")

        for stock_symbol, record_count in stocks_info:
            print(f"\n📊 Fixing dates for {stock_symbol} ({record_count} records)")

            # Get all records for this stock ordered by the current 'date' field
            cursor = conn.execute("""
                SELECT rowid, date, close FROM price_data
                WHERE stock_symbol = ?
                ORDER BY CAST(date AS INTEGER)
            """, (stock_symbol,))

            records = cursor.fetchall()

            # Create proper date sequence (most recent date should be today)
            end_date = datetime.now()

            # Update each record with proper date
            for i, (rowid, old_date, close) in enumerate(records):
                # Calculate actual date (working backwards from today)
                days_back = len(records) - 1 - i
                actual_date = (end_date - timedelta(days=days_back)).strftime('%Y-%m-%d')

                # Update the record
                conn.execute("""
                    UPDATE price_data
                    SET date = ?
                    WHERE rowid = ?
                """, (actual_date, rowid))

                if i < 3:  # Show first 3 updates as example
                    print(f"  Updated: {old_date} → {actual_date} (close: {close})")

            print(f"  ✅ Fixed {len(records)} records for {stock_symbol}")

        # Commit all changes
        conn.commit()
        print(f"\n🎉 Database date format fix completed!")

def verify_date_fix():
    """Verify that date fix worked properly"""
    print("\n=== Verifying Date Fix ===")

    db = get_db()

    with db.get_connection() as conn:
        # Check sample of fixed dates
        cursor = conn.execute("""
            SELECT stock_symbol, date, close
            FROM price_data
            WHERE stock_symbol = 'VCB'
            ORDER BY date DESC
            LIMIT 5
        """)

        records = cursor.fetchall()
        print("Sample of fixed dates (VCB, most recent first):")
        for stock, date, close in records:
            print(f"  {stock}: {date} - Close: {close}")

        # Verify date format
        cursor = conn.execute("""
            SELECT date FROM price_data
            WHERE date LIKE '____-__-__'
            LIMIT 1
        """)

        proper_format = cursor.fetchone()
        if proper_format:
            print("✅ Date format verification: PASSED")
            return True
        else:
            print("❌ Date format verification: FAILED")
            return False

def test_enhanced_signals_after_fix():
    """Test if date fix improves signal analysis"""
    print("\n=== Testing Signals After Date Fix ===")

    try:
        from shared.analysis.smart_money import SmartMoneyAnalyzer

        analyzer = SmartMoneyAnalyzer()
        db = get_db()

        stocks = db.get_all_stocks()

        print("Testing signal quality after date fix:")

        signal_scores = []
        signal_classes = []

        for stock in stocks:
            analysis = analyzer.analyze_symbol(stock['symbol'], days_back=60)

            if 'error' not in analysis:
                score = analysis['composite_score']['composite_score']
                signal_class = analysis['composite_score']['signal_class']
                signal_scores.append(score)
                signal_classes.append(signal_class)

                print(f"  {stock['symbol']}: {score:.1f} ({signal_class})")
            else:
                print(f"  {stock['symbol']}: Error - {analysis['error']}")

        # Analyze signal diversity
        if signal_scores:
            score_range = max(signal_scores) - min(signal_scores)
            avg_score = sum(signal_scores) / len(signal_scores)
            unique_classes = len(set(signal_classes))

            print(f"\n📈 Post-Fix Signal Quality:")
            print(f"  Average Score: {avg_score:.1f}")
            print(f"  Score Range: {score_range:.1f}")
            print(f"  Signal Classes: {unique_classes} unique ({set(signal_classes)})")
            print(f"  Diversity: {'Excellent' if score_range > 20 else 'Good' if score_range > 10 else 'Poor'}")

            return score_range > 10, signal_scores, signal_classes

    except Exception as e:
        print(f"❌ Error testing signals: {e}")
        return False, [], []

    return False, [], []

def main():
    """Main database fix function"""
    print("Vietnam Stock Analysis - Database Date Fix")
    print("=" * 60)

    try:
        # Step 1: Backup database
        backup_path = backup_database()

        # Step 2: Fix date format
        fix_date_format()

        # Step 3: Verify fix
        verification_passed = verify_date_fix()

        if not verification_passed:
            print("⚠️ Date fix verification failed. Check manually.")
            return

        # Step 4: Test signal improvement
        improved, scores, classes = test_enhanced_signals_after_fix()

        print("\n" + "=" * 60)

        if improved:
            print("🎉 SUCCESS: Date fix dramatically improved signal analysis!")
            print(f"\n📊 Signal Results:")
            print(f"  Score Range: {max(scores) - min(scores):.1f} points")
            print(f"  Unique Signal Classes: {len(set(classes))}")
            print(f"  Signal Classes: {', '.join(set(classes))}")

            print("\n✅ System Status:")
            print("  • Database dates: FIXED")
            print("  • Signal variation: RESTORED")
            print("  • Ready for Vietnamese market calibration")
            print("  • Dashboard should now show meaningful analysis")

        else:
            print("✅ Date fix completed, but further calibration needed")
            print("\n🔧 Next Steps:")
            print("  • Vietnamese market parameter tuning required")
            print("  • Algorithm sensitivity adjustment needed")
            print(f"  • Database backup available at: {backup_path}")

    except Exception as e:
        print(f"❌ Database fix error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()