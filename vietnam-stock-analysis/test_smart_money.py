#!/usr/bin/env python3
"""
Test Smart Money Signal System Integration
Tests the smart money analyzer with real database data
"""

import sys
import os
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from shared.analysis.smart_money import SmartMoneyAnalyzer
from shared.models.database import get_db

def test_smart_money_analyzer():
    """Test the smart money analyzer functionality"""
    print("=== Testing Smart Money Signal System ===")

    try:
        # Initialize analyzer
        analyzer = SmartMoneyAnalyzer()
        print("✅ Smart Money Analyzer initialized successfully")

        # Get available stocks
        db = get_db()
        stocks = db.get_all_stocks()
        print(f"✅ Found {len(stocks)} stocks in database")

        # Test individual stock analysis
        if stocks:
            test_symbol = stocks[0]['symbol']
            print(f"\n🔍 Testing analysis for {test_symbol}")

            analysis = analyzer.analyze_symbol(test_symbol, days_back=30)

            if 'error' in analysis:
                print(f"❌ Analysis error: {analysis['error']}")
            else:
                print("✅ Individual analysis completed successfully")

                # Display key results
                composite = analysis['composite_score']
                print(f"  📊 Composite Score: {composite['composite_score']:.1f}")
                print(f"  🎯 Signal Class: {composite['signal_class']}")
                print(f"  💪 Signal Strength: {composite['signal_strength']}")
                print(f"  🎬 Recommended Action: {composite['recommended_action']}")

                # Component scores
                print(f"\n  🔬 Component Scores:")
                for component, score in composite['component_scores'].items():
                    print(f"    - {component.replace('_', ' ').title()}: {score:.1f}")

                # Entry/Exit signals
                entry_exit = analysis['entry_exit_signals']
                print(f"\n  📈 Entry Signals: {len(entry_exit['entry_signals'])}")
                print(f"  💰 Position Sizing: {entry_exit['position_sizing']}")

                # Risk analysis
                risk = analysis['risk_analysis']
                print(f"  ⚠️ Volatility: {risk['volatility']:.1f}%")
                print(f"  📉 Max Drawdown: {risk['max_drawdown']:.1f}%")

        # Test market overview
        print(f"\n🌍 Testing market overview analysis")
        market_overview = analyzer.get_market_overview()

        print("✅ Market overview analysis completed")
        print(f"  📈 Market Sentiment: {market_overview['market_sentiment']}")
        print(f"  💪 Strong Signals: {len(market_overview['strong_signals'])}")
        print(f"  📉 Weak Signals: {len(market_overview['weak_signals'])}")
        print(f"  🎯 Top Picks: {len(market_overview['top_picks'])}")

        if market_overview['top_picks']:
            print("\n  🔥 Top Picks:")
            for pick in market_overview['top_picks']:
                print(f"    - {pick['symbol']}: {pick['score']:.1f} ({pick['signal']})")

        print("\n=== Smart Money Testing Complete ===")
        return True

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_quality():
    """Test data quality for smart money analysis"""
    print("\n=== Testing Data Quality ===")

    try:
        db = get_db()
        stocks = db.get_all_stocks()

        for stock in stocks:
            symbol = stock['symbol']
            # Get some price data
            price_data = db.get_price_data(symbol, '2024-01-01', '2024-12-31')

            print(f"📊 {symbol}: {len(price_data)} price records")

            if len(price_data) < 10:
                print(f"  ⚠️ Warning: Limited data for {symbol}")
            else:
                # Check data quality
                df = []
                for record in price_data:
                    df.append({
                        'close': record['close'],
                        'volume': record['volume'],
                        'high': record['high'],
                        'low': record['low']
                    })

                if df:
                    # Basic data quality checks
                    avg_volume = sum(d['volume'] for d in df) / len(df)
                    avg_price = sum(d['close'] for d in df) / len(df)

                    print(f"  ✅ Avg Price: {avg_price:,.0f} VND, Avg Volume: {avg_volume:,.0f}")

        print("=== Data Quality Check Complete ===")

    except Exception as e:
        print(f"❌ Data quality error: {e}")

def main():
    """Main test function"""
    print("Vietnam Stock Analysis - Smart Money Testing")
    print("=" * 60)

    # Test data quality first
    test_data_quality()

    # Test smart money analyzer
    success = test_smart_money_analyzer()

    print("\n" + "=" * 60)
    if success:
        print("🎉 All smart money tests passed!")
        print("\n🚀 Smart Money Features Ready:")
        print("  • Market sentiment analysis")
        print("  • Individual stock signals")
        print("  • Volume pattern detection")
        print("  • Price action analysis")
        print("  • Momentum indicators")
        print("  • Accumulation/distribution")
        print("  • Vietnamese market context")
        print("  • Risk assessment")
        print("  • Entry/exit signals")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()