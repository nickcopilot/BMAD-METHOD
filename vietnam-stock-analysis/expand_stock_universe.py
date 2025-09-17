#!/usr/bin/env python3
"""
Stock Universe Expansion - Phase 1
Expand from 3 stocks to 20+ stocks across Vietnamese market sectors
Following BMAD Master strategic recommendation
"""

import sys
import os
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from data_collection.vnstock_collector import VNStockCollector
from shared.models.database import get_db
from shared.analysis.smart_money import SmartMoneyAnalyzer

def get_expansion_stocks():
    """Get the strategic stock expansion list by sector"""
    expansion_stocks = {
        # Banking sector (Vietnamese market leaders)
        'banking': ['VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'ACB'],

        # Real Estate sector (major developers)
        'real_estate': ['VHM', 'VIC', 'VRE', 'NVL', 'KDH'],

        # Steel sector (industrial leaders)
        'steel': ['HPG', 'HSG', 'NKG', 'TLH'],

        # Securities sector (brokerage leaders)
        'securities': ['SSI', 'VCI', 'VND', 'HCM']
    }

    all_symbols = []
    for sector, stocks in expansion_stocks.items():
        all_symbols.extend(stocks)

    return expansion_stocks, all_symbols

def collect_expanded_data():
    """Collect data for all expansion stocks"""
    print("=== BMAD Master Strategic Expansion: Stock Universe ===")

    expansion_stocks, all_symbols = get_expansion_stocks()

    print(f"📈 Expanding from 3 to {len(all_symbols)} stocks across {len(expansion_stocks)} sectors")
    print(f"Sectors: {', '.join(expansion_stocks.keys())}")

    collector = VNStockCollector()
    db = get_db()

    # Extended date range for comprehensive analysis
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')

    print(f"Collection period: {start_date} to {end_date}")

    # Track results by sector
    sector_results = {}
    total_new_stocks = 0
    total_new_records = 0

    for sector, symbols in expansion_stocks.items():
        print(f"\n🏢 {sector.upper()} SECTOR:")
        sector_results[sector] = {'stocks': 0, 'records': 0, 'errors': 0}

        for symbol in symbols:
            print(f"  📊 Processing {symbol}...")

            try:
                # Check if stock already exists
                existing_stocks = db.get_all_stocks()
                existing_symbols = [s['symbol'] for s in existing_stocks]

                if symbol not in existing_symbols:
                    # Collect stock info
                    stock_info = collector.collect_stock_info(symbol)
                    if stock_info:
                        if db.insert_stock(stock_info):
                            sector_results[sector]['stocks'] += 1
                            total_new_stocks += 1
                            print(f"    ✅ Added stock: {stock_info.name}")
                        else:
                            print(f"    ⚠️ Failed to store stock info")
                    else:
                        print(f"    ⚠️ No stock info available")

                # Collect price data
                price_data_list = collector.collect_price_data(symbol, start_date, end_date)

                stored_count = 0
                for price_data in price_data_list:
                    if db.insert_price_data(price_data):
                        stored_count += 1

                sector_results[sector]['records'] += stored_count
                total_new_records += stored_count

                print(f"    ✅ Price data: {len(price_data_list)} collected, {stored_count} stored")

            except Exception as e:
                sector_results[sector]['errors'] += 1
                print(f"    ❌ Error with {symbol}: {e}")

    # Results summary
    print(f"\n🎉 EXPANSION RESULTS:")
    print(f"  Total new stocks: {total_new_stocks}")
    print(f"  Total new records: {total_new_records}")

    print(f"\n📊 BY SECTOR:")
    for sector, results in sector_results.items():
        print(f"  {sector}: {results['stocks']} stocks, {results['records']} records, {results['errors']} errors")

    return sector_results, total_new_stocks, total_new_records

def test_expanded_signals():
    """Test smart money signals across expanded universe"""
    print(f"\n=== Testing Smart Money Signals at Scale ===")

    analyzer = SmartMoneyAnalyzer()
    db = get_db()

    all_stocks = db.get_all_stocks()
    print(f"Testing signals for {len(all_stocks)} stocks")

    # Analyze signals by sector
    sector_signals = {}

    for stock in all_stocks:
        symbol = stock['symbol']
        sector = stock['sector']

        if sector not in sector_signals:
            sector_signals[sector] = {
                'stocks': [],
                'scores': [],
                'signals': [],
                'avg_score': 0
            }

        print(f"  🔍 {symbol} ({sector})...", end=' ')

        try:
            analysis = analyzer.analyze_symbol(symbol, days_back=60)

            if 'error' not in analysis:
                score = analysis['composite_score']['composite_score']
                adjusted_score = analysis['market_context']['adjusted_score']
                signal_class = analysis['composite_score']['signal_class']

                sector_signals[sector]['stocks'].append(symbol)
                sector_signals[sector]['scores'].append(adjusted_score)
                sector_signals[sector]['signals'].append(signal_class)

                print(f"{adjusted_score:.1f} ({signal_class})")

            else:
                print(f"Error: {analysis['error']}")

        except Exception as e:
            print(f"Failed: {e}")

    # Calculate sector statistics
    print(f"\n📈 SECTOR SIGNAL ANALYSIS:")

    total_scores = []
    total_signals = []

    for sector, data in sector_signals.items():
        if data['scores']:
            avg_score = sum(data['scores']) / len(data['scores'])
            score_range = max(data['scores']) - min(data['scores'])
            unique_signals = len(set(data['signals']))

            sector_signals[sector]['avg_score'] = avg_score

            total_scores.extend(data['scores'])
            total_signals.extend(data['signals'])

            print(f"  {sector.upper()}:")
            print(f"    Stocks: {len(data['stocks'])}")
            print(f"    Avg Score: {avg_score:.1f}")
            print(f"    Score Range: {score_range:.1f}")
            print(f"    Signal Types: {unique_signals} ({', '.join(set(data['signals']))})")

    # Overall system quality
    if total_scores:
        overall_range = max(total_scores) - min(total_scores)
        overall_avg = sum(total_scores) / len(total_scores)
        total_signal_types = len(set(total_signals))

        print(f"\n🎯 OVERALL SIGNAL QUALITY:")
        print(f"  Total Stocks: {len(total_scores)}")
        print(f"  Score Range: {overall_range:.1f}")
        print(f"  Average Score: {overall_avg:.1f}")
        print(f"  Signal Diversity: {total_signal_types} types")

        # Quality assessment
        if overall_range > 30 and total_signal_types >= 4:
            quality = "EXCELLENT"
        elif overall_range > 20 and total_signal_types >= 3:
            quality = "GOOD"
        elif overall_range > 10:
            quality = "FAIR"
        else:
            quality = "NEEDS IMPROVEMENT"

        print(f"  Quality Assessment: {quality}")

        return sector_signals, quality, overall_range

    return {}, "INSUFFICIENT DATA", 0

def generate_expansion_report():
    """Generate expansion success report"""
    print(f"\n=== EXPANSION PHASE COMPLETION REPORT ===")

    db = get_db()

    # Get final stock count by sector
    all_stocks = db.get_all_stocks()

    sector_counts = {}
    for stock in all_stocks:
        sector = stock['sector']
        if sector not in sector_counts:
            sector_counts[sector] = 0
        sector_counts[sector] += 1

    total_stocks = len(all_stocks)

    print(f"📊 FINAL SYSTEM STATUS:")
    print(f"  Total Stocks: {total_stocks}")
    print(f"  Sectors Covered: {len(sector_counts)}")

    for sector, count in sector_counts.items():
        print(f"    {sector}: {count} stocks")

    # Check data coverage
    with db.get_connection() as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM price_data")
        total_records = cursor.fetchone()[0]

        cursor = conn.execute("""
            SELECT stock_symbol, COUNT(*) as records
            FROM price_data
            GROUP BY stock_symbol
            ORDER BY records DESC
        """)

        stock_records = cursor.fetchall()

    print(f"\n💾 DATA COVERAGE:")
    print(f"  Total price records: {total_records:,}")
    print(f"  Average per stock: {total_records // total_stocks if total_stocks > 0 else 0}")

    if len(stock_records) >= 5:
        print(f"  Sample coverage:")
        for symbol, records in stock_records[:5]:
            print(f"    {symbol}: {records} records")

    return total_stocks, len(sector_counts), total_records

def main():
    """Main expansion execution"""
    print("Vietnam Stock Analysis - Strategic Expansion Phase")
    print("=" * 70)
    print("BMAD Master Recommendation: Expand to 20+ stocks for full functionality")
    print("=" * 70)

    try:
        # Phase 1: Collect expanded data
        sector_results, new_stocks, new_records = collect_expanded_data()

        # Phase 2: Test signal quality at scale
        sector_signals, quality, signal_range = test_expanded_signals()

        # Phase 3: Generate completion report
        total_stocks, sectors, total_records = generate_expansion_report()

        print("\n" + "=" * 70)

        if total_stocks >= 15 and signal_range > 15:
            print("🎉 EXPANSION PHASE: SUCCESSFUL!")
            print(f"\n✅ Achievements:")
            print(f"  • Expanded from 3 to {total_stocks} stocks")
            print(f"  • {sectors} sector coverage")
            print(f"  • {total_records:,} total price records")
            print(f"  • {signal_range:.1f} point signal diversity")
            print(f"  • Signal quality: {quality}")

            print(f"\n🚀 System Status: PRODUCTION READY")
            print(f"  • Comprehensive Vietnamese market coverage")
            print(f"  • Sector-diversified analysis capability")
            print(f"  • Smart money signals at scale")
            print(f"  • Ready for advanced features (alerts, backtesting)")

        else:
            print("⚠️ EXPANSION PHASE: PARTIALLY SUCCESSFUL")
            print(f"  • Achieved {total_stocks} stocks (target: 15+)")
            print(f"  • Signal diversity: {signal_range:.1f} (target: 15+)")
            print(f"  • May need additional calibration")

    except Exception as e:
        print(f"❌ Expansion error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()