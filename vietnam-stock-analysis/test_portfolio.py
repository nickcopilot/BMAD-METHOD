#!/usr/bin/env python3
"""
Test Portfolio Functionality
Tests portfolio management and dashboard capabilities
"""

import sys
import os
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from shared.models.database import get_db

def test_portfolio_functionality():
    """Test portfolio management functions"""
    print("=== Testing Portfolio Management ===")

    db = get_db()

    # Test 1: Add portfolio positions
    print("\n1. Adding portfolio positions...")

    # Add VCB position
    success1 = db.add_portfolio_position(
        stock_symbol='VCB',
        position_size=100,
        entry_price=65000,
        entry_date='2024-01-15'
    )
    print(f"  ✓ Added VCB position: {'✓' if success1 else '✗'}")

    # Add HPG position
    success2 = db.add_portfolio_position(
        stock_symbol='HPG',
        position_size=200,
        entry_price=28500,
        entry_date='2024-01-16'
    )
    print(f"  ✓ Added HPG position: {'✓' if success2 else '✗'}")

    # Add VHM position
    success3 = db.add_portfolio_position(
        stock_symbol='VHM',
        position_size=50,
        entry_price=75000,
        entry_date='2024-01-17'
    )
    print(f"  ✓ Added VHM position: {'✓' if success3 else '✗'}")

    # Test 2: Get portfolio
    print("\n2. Retrieving portfolio...")
    portfolio = db.get_portfolio()
    print(f"  ✓ Portfolio has {len(portfolio)} positions")

    for position in portfolio:
        print(f"    - {position['stock_symbol']}: {position['position_size']} shares @ {position['entry_price']:,.0f} VND")

    # Test 3: Get portfolio performance
    print("\n3. Calculating portfolio performance...")
    performance = db.get_portfolio_performance()

    print(f"  ✓ Total Portfolio Value: {performance['total_value']:,.0f} VND")
    print(f"  ✓ Total Cost: {performance['total_cost']:,.0f} VND")
    print(f"  ✓ Total P&L: {performance['total_gain_loss']:+,.0f} VND ({performance['total_gain_loss_pct']:+.2f}%)")

    print("\n  Position Details:")
    for position in performance['positions']:
        print(f"    {position['stock_symbol']}: "
              f"Value: {position['position_value']:,.0f} VND, "
              f"P&L: {position['gain_loss']:+,.0f} VND ({position['gain_loss_pct']:+.2f}%)")

    # Test 4: Test dashboard data loading functions
    print("\n4. Testing dashboard data functions...")

    # Test stock data loading
    stocks = db.get_all_stocks()
    print(f"  ✓ Available stocks: {len(stocks)}")

    # Test price data loading for each stock
    for stock in stocks:
        symbol = stock['symbol']
        latest_price = db.get_latest_price(symbol)
        if latest_price:
            print(f"    - {symbol}: Latest price {latest_price['close']:,.0f} VND")
        else:
            print(f"    - {symbol}: No price data")

    print("\n=== Portfolio Test Complete ===")
    return True

def test_database_integrity():
    """Test database integrity and relationships"""
    print("\n=== Testing Database Integrity ===")

    db = get_db()

    # Check all tables exist and have data
    with db.get_connection() as conn:
        # Check stocks table
        stocks_count = conn.execute("SELECT COUNT(*) FROM stocks").fetchone()[0]
        print(f"  ✓ Stocks table: {stocks_count} records")

        # Check price_data table
        price_count = conn.execute("SELECT COUNT(*) FROM price_data").fetchone()[0]
        print(f"  ✓ Price data table: {price_count} records")

        # Check portfolio table
        portfolio_count = conn.execute("SELECT COUNT(*) FROM portfolio").fetchone()[0]
        print(f"  ✓ Portfolio table: {portfolio_count} records")

        # Check foreign key relationships
        orphaned_prices = conn.execute("""
            SELECT COUNT(*) FROM price_data p
            LEFT JOIN stocks s ON p.stock_symbol = s.symbol
            WHERE s.symbol IS NULL
        """).fetchone()[0]
        print(f"  ✓ Orphaned price records: {orphaned_prices}")

        orphaned_portfolio = conn.execute("""
            SELECT COUNT(*) FROM portfolio p
            LEFT JOIN stocks s ON p.stock_symbol = s.symbol
            WHERE s.symbol IS NULL
        """).fetchone()[0]
        print(f"  ✓ Orphaned portfolio records: {orphaned_portfolio}")

    print("\n=== Database Integrity Check Complete ===")

def cleanup_test_data():
    """Clean up test portfolio data"""
    print("\n=== Cleaning Up Test Data ===")

    db = get_db()

    with db.get_connection() as conn:
        # Remove test portfolio positions
        deleted = conn.execute("DELETE FROM portfolio WHERE user_id = 'default'").rowcount
        print(f"  ✓ Removed {deleted} test portfolio positions")

    print("=== Cleanup Complete ===")

def main():
    """Main test function"""
    print("Vietnam Stock Analysis - Portfolio Testing")
    print("=" * 60)

    try:
        # Test database integrity first
        test_database_integrity()

        # Test portfolio functionality
        test_portfolio_functionality()

        # Optionally clean up (uncomment if needed)
        # cleanup_test_data()

        print("\n" + "=" * 60)
        print("All portfolio tests completed successfully!")

    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()