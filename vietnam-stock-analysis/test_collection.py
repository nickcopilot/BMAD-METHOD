#!/usr/bin/env python3
"""
Test Data Collection Service
Tests the complete data collection pipeline with database storage
"""

import sys
import os
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from data_collection.vnstock_collector import VNStockCollector
from data_collection.gso_collector import GSOCollector
from shared.models.database import get_db

def test_stock_collection():
    """Test stock data collection and storage"""
    print("=== Testing Stock Data Collection ===")

    collector = VNStockCollector()
    db = get_db()

    # Test with a few symbols
    test_symbols = ['VCB', 'HPG', 'VHM']

    for symbol in test_symbols:
        print(f"\nTesting {symbol}:")

        # Test stock info collection
        stock = collector.collect_stock_info(symbol)
        if stock:
            success = db.insert_stock(stock)
            print(f"  ✓ Stock info: {stock.name} ({'✓ stored' if success else '✗ failed to store'})")
        else:
            print(f"  ✗ Failed to collect stock info")

        # Test price data collection (last 7 days)
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

        price_data_list = collector.collect_price_data(symbol, start_date, end_date)
        stored_count = 0
        for price_data in price_data_list:
            if db.insert_price_data(price_data):
                stored_count += 1

        print(f"  ✓ Price data: {len(price_data_list)} collected, {stored_count} stored")

    print("\n=== Stock Collection Test Complete ===\n")

def test_database_queries():
    """Test database query functions"""
    print("=== Testing Database Queries ===")

    db = get_db()

    # Test stock queries
    banking_stocks = db.get_stocks_by_sector('banking')
    print(f"Banking stocks in database: {len(banking_stocks)}")

    if banking_stocks:
        for stock in banking_stocks[:3]:  # Show first 3
            print(f"  - {stock['symbol']}: {stock['name']}")

    # Test price data queries
    if banking_stocks:
        symbol = banking_stocks[0]['symbol']
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        price_data = db.get_price_data(symbol, start_date, end_date)
        print(f"Price records for {symbol}: {len(price_data)}")

        if price_data:
            latest = price_data[0]
            print(f"  Latest: {latest['date']} - Close: {latest['close']:,.0f} VND")

    print("\n=== Database Query Test Complete ===\n")

def test_gso_collection():
    """Test GSO economic data collection"""
    print("=== Testing GSO Data Collection ===")

    collector = GSOCollector()

    # Test connection
    if collector.test_connection():
        print("✓ GSO connection successful")

        # Test data collection
        results = collector.run_weekly_collection()
        print(f"GSO collection results: {results}")
    else:
        print("✗ GSO connection failed")

    print("\n=== GSO Collection Test Complete ===\n")

def test_validation():
    """Test data validation"""
    print("=== Testing Data Validation ===")

    from shared.utils.validators import validate_data_batch

    # Test stock validation
    test_stock_data = [{
        'symbol': 'VCB',
        'name': 'Vietcombank',
        'sector': 'banking',
        'exchange': 'HOSE',
        'market_cap': 1000000000000
    }]

    valid_stocks, stock_errors = validate_data_batch(test_stock_data, 'stock_data')
    print(f"Stock validation: {len(valid_stocks)} valid, {len(stock_errors)} errors")

    # Test price validation
    test_price_data = [{
        'stock_symbol': 'VCB',
        'date': '2024-01-15',
        'open': 85000,
        'high': 86000,
        'low': 84000,
        'close': 85500,
        'volume': 1000000
    }]

    valid_prices, price_errors = validate_data_batch(test_price_data, 'price_data')
    print(f"Price validation: {len(valid_prices)} valid, {len(price_errors)} errors")

    if stock_errors:
        print("Stock validation errors:")
        for error in stock_errors:
            print(f"  - {error}")

    if price_errors:
        print("Price validation errors:")
        for error in price_errors:
            print(f"  - {error}")

    print("\n=== Validation Test Complete ===\n")

def main():
    """Run all tests"""
    print("Vietnam Stock Analysis - Data Collection Tests")
    print("=" * 60)

    try:
        # Test data validation first
        test_validation()

        # Test stock data collection
        test_stock_collection()

        # Test database queries
        test_database_queries()

        # Test GSO collection (might fail due to network/website changes)
        test_gso_collection()

        print("=" * 60)
        print("All tests completed!")

    except Exception as e:
        print(f"Test error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()