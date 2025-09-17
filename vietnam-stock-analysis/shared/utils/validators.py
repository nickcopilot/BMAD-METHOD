"""
Data Validation Utilities
Validates data quality and consistency for Vietnamese stock analysis
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
import re

# Configure logging
logger = logging.getLogger(__name__)

class DataValidator:
    """Validates financial and economic data for quality and consistency"""

    def __init__(self):
        self.validation_errors = []

    def validate_stock_data(self, stock_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate basic stock information"""
        errors = []

        # Required fields
        required_fields = ['symbol', 'name', 'sector', 'exchange']
        for field in required_fields:
            if not stock_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Symbol format (Vietnamese stocks: 3-4 characters)
        symbol = stock_data.get('symbol', '')
        if not re.match(r'^[A-Z]{3,4}$', symbol):
            errors.append(f"Invalid symbol format: {symbol}")

        # Valid exchanges
        valid_exchanges = ['HOSE', 'HNX', 'UPCOM']
        exchange = stock_data.get('exchange', '')
        if exchange not in valid_exchanges:
            errors.append(f"Invalid exchange: {exchange}")

        # Valid sectors
        valid_sectors = ['securities', 'banking', 'real_estate', 'steel']
        sector = stock_data.get('sector', '')
        if sector not in valid_sectors:
            errors.append(f"Invalid sector: {sector}")

        # Market cap should be positive
        market_cap = stock_data.get('market_cap', 0)
        if market_cap < 0:
            errors.append(f"Negative market cap: {market_cap}")

        return len(errors) == 0, errors

    def validate_price_data(self, price_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate price and volume data"""
        errors = []

        # Required fields
        required_fields = ['stock_symbol', 'date', 'open', 'high', 'low', 'close', 'volume']
        for field in required_fields:
            if price_data.get(field) is None:
                errors.append(f"Missing required field: {field}")

        # Price validations
        open_price = price_data.get('open', 0)
        high_price = price_data.get('high', 0)
        low_price = price_data.get('low', 0)
        close_price = price_data.get('close', 0)

        # Prices should be positive
        for price, name in [(open_price, 'open'), (high_price, 'high'),
                           (low_price, 'low'), (close_price, 'close')]:
            if price <= 0:
                errors.append(f"Invalid {name} price: {price}")

        # High should be >= Low
        if high_price < low_price:
            errors.append(f"High price ({high_price}) less than low price ({low_price})")

        # High should be >= Open and Close
        if high_price < open_price:
            errors.append(f"High price ({high_price}) less than open price ({open_price})")
        if high_price < close_price:
            errors.append(f"High price ({high_price}) less than close price ({close_price})")

        # Low should be <= Open and Close
        if low_price > open_price:
            errors.append(f"Low price ({low_price}) greater than open price ({open_price})")
        if low_price > close_price:
            errors.append(f"Low price ({low_price}) greater than close price ({close_price})")

        # Volume should be non-negative
        volume = price_data.get('volume', 0)
        if volume < 0:
            errors.append(f"Negative volume: {volume}")

        # Date format validation
        date_str = price_data.get('date', '')
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Date shouldn't be in the future
            if date_obj > datetime.now():
                errors.append(f"Future date: {date_str}")
            # Date shouldn't be too old (more than 10 years)
            if date_obj < datetime.now() - timedelta(days=3650):
                errors.append(f"Date too old: {date_str}")
        except ValueError:
            errors.append(f"Invalid date format: {date_str}")

        # Price change validation (if previous close available)
        # This would require database lookup, implement later

        return len(errors) == 0, errors

    def validate_financial_data(self, financial_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate financial statement data"""
        errors = []

        # Required fields
        required_fields = ['stock_symbol', 'period', 'period_type']
        for field in required_fields:
            if not financial_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Valid period types
        period_type = financial_data.get('period_type', '')
        if period_type not in ['quarterly', 'annual']:
            errors.append(f"Invalid period type: {period_type}")

        # Period format validation
        period = financial_data.get('period', '')
        if period_type == 'quarterly':
            if not re.match(r'^Q[1-4]-\d{4}$', period):
                errors.append(f"Invalid quarterly period format: {period}")
        elif period_type == 'annual':
            if not re.match(r'^\d{4}$', period):
                errors.append(f"Invalid annual period format: {period}")

        # Financial ratio validations
        roe = financial_data.get('roe')
        if roe is not None and (roe < -100 or roe > 100):
            errors.append(f"ROE out of reasonable range: {roe}%")

        roa = financial_data.get('roa')
        if roa is not None and (roa < -50 or roa > 50):
            errors.append(f"ROA out of reasonable range: {roa}%")

        pe_ratio = financial_data.get('pe_ratio')
        if pe_ratio is not None and (pe_ratio < 0 or pe_ratio > 1000):
            errors.append(f"PE ratio out of reasonable range: {pe_ratio}")

        pb_ratio = financial_data.get('pb_ratio')
        if pb_ratio is not None and (pb_ratio < 0 or pb_ratio > 100):
            errors.append(f"PB ratio out of reasonable range: {pb_ratio}")

        return len(errors) == 0, errors

    def validate_economic_data(self, economic_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Validate economic indicator data"""
        errors = []

        # Required fields
        required_fields = ['indicator_code', 'indicator_name', 'period', 'value', 'source']
        for field in required_fields:
            if not economic_data.get(field):
                errors.append(f"Missing required field: {field}")

        # Valid sources
        valid_sources = ['GSO', 'SBV', 'MINISTRY_OF_FINANCE']
        source = economic_data.get('source', '')
        if source not in valid_sources:
            errors.append(f"Invalid source: {source}")

        # Valid categories
        valid_categories = ['growth', 'inflation', 'monetary', 'fiscal', 'trade']
        category = economic_data.get('category', '')
        if category not in valid_categories:
            errors.append(f"Invalid category: {category}")

        # Value range validations based on indicator type
        indicator_code = economic_data.get('indicator_code', '')
        value = economic_data.get('value')

        if value is not None:
            if indicator_code == 'GDP_GROWTH' and (value < -20 or value > 20):
                errors.append(f"GDP growth out of reasonable range: {value}%")
            elif indicator_code == 'CPI_INFLATION' and (value < -10 or value > 30):
                errors.append(f"Inflation out of reasonable range: {value}%")
            elif indicator_code == 'INTEREST_RATE' and (value < 0 or value > 25):
                errors.append(f"Interest rate out of reasonable range: {value}%")

        return len(errors) == 0, errors

    def validate_data_consistency(self, data_list: List[Dict[str, Any]],
                                 data_type: str) -> Tuple[bool, List[str]]:
        """Validate consistency across multiple data points"""
        errors = []

        if not data_list:
            return True, []

        if data_type == 'price_data':
            # Check for gaps in price data
            dates = [datetime.strptime(d['date'], '%Y-%m-%d') for d in data_list if d.get('date')]
            dates.sort()

            for i in range(1, len(dates)):
                gap = (dates[i] - dates[i-1]).days
                # Allow for weekends and holidays, but flag gaps > 5 days
                if gap > 5:
                    errors.append(f"Large gap in price data: {gap} days between {dates[i-1].date()} and {dates[i].date()}")

            # Check for duplicate dates
            date_strings = [d['date'] for d in data_list if d.get('date')]
            if len(date_strings) != len(set(date_strings)):
                errors.append("Duplicate dates found in price data")

        elif data_type == 'financial_data':
            # Check for logical progression in financial metrics
            symbol_data = {}
            for item in data_list:
                symbol = item.get('stock_symbol')
                if symbol not in symbol_data:
                    symbol_data[symbol] = []
                symbol_data[symbol].append(item)

            for symbol, symbol_items in symbol_data.items():
                # Sort by period
                symbol_items.sort(key=lambda x: x.get('period', ''))

                # Check for reasonable changes in key metrics
                for i in range(1, len(symbol_items)):
                    prev_item = symbol_items[i-1]
                    curr_item = symbol_items[i]

                    # Check revenue growth (shouldn't change more than 500% quarter to quarter)
                    prev_revenue = prev_item.get('revenue', 0)
                    curr_revenue = curr_item.get('revenue', 0)

                    if prev_revenue > 0 and curr_revenue > 0:
                        growth = abs((curr_revenue - prev_revenue) / prev_revenue)
                        if growth > 5:  # 500% change
                            errors.append(f"Unusual revenue change for {symbol}: {growth:.1%}")

        return len(errors) == 0, errors

    def clean_data(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """Clean and normalize data"""
        cleaned_data = data.copy()

        if data_type == 'stock_data':
            # Normalize symbol to uppercase
            if 'symbol' in cleaned_data:
                cleaned_data['symbol'] = cleaned_data['symbol'].upper().strip()

            # Normalize exchange
            if 'exchange' in cleaned_data:
                cleaned_data['exchange'] = cleaned_data['exchange'].upper().strip()

        elif data_type == 'price_data':
            # Ensure numeric fields are float/int
            numeric_fields = ['open', 'high', 'low', 'close', 'volume', 'value', 'foreign_buy', 'foreign_sell']
            for field in numeric_fields:
                if field in cleaned_data and cleaned_data[field] is not None:
                    try:
                        if field == 'volume':
                            cleaned_data[field] = int(float(cleaned_data[field]))
                        else:
                            cleaned_data[field] = float(cleaned_data[field])
                    except (ValueError, TypeError):
                        logger.warning(f"Could not convert {field} to numeric: {cleaned_data[field]}")

        elif data_type == 'economic_data':
            # Normalize source
            if 'source' in cleaned_data:
                cleaned_data['source'] = cleaned_data['source'].upper().strip()

            # Ensure value is numeric
            if 'value' in cleaned_data and cleaned_data['value'] is not None:
                try:
                    cleaned_data['value'] = float(cleaned_data['value'])
                except (ValueError, TypeError):
                    logger.warning(f"Could not convert value to numeric: {cleaned_data['value']}")

        return cleaned_data

    def get_validation_summary(self) -> Dict[str, Any]:
        """Get summary of all validation errors"""
        return {
            'total_errors': len(self.validation_errors),
            'errors': self.validation_errors
        }


def validate_data_batch(data_list: List[Dict[str, Any]], data_type: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """Validate and clean a batch of data"""
    validator = DataValidator()
    valid_data = []
    all_errors = []

    for i, item in enumerate(data_list):
        # Clean data first
        cleaned_item = validator.clean_data(item, data_type)

        # Validate based on type
        if data_type == 'stock_data':
            is_valid, errors = validator.validate_stock_data(cleaned_item)
        elif data_type == 'price_data':
            is_valid, errors = validator.validate_price_data(cleaned_item)
        elif data_type == 'financial_data':
            is_valid, errors = validator.validate_financial_data(cleaned_item)
        elif data_type == 'economic_data':
            is_valid, errors = validator.validate_economic_data(cleaned_item)
        else:
            is_valid, errors = False, [f"Unknown data type: {data_type}"]

        if is_valid:
            valid_data.append(cleaned_item)
        else:
            all_errors.extend([f"Item {i}: {error}" for error in errors])

    # Additional consistency validation
    if valid_data:
        is_consistent, consistency_errors = validator.validate_data_consistency(valid_data, data_type)
        if not is_consistent:
            all_errors.extend(consistency_errors)

    return valid_data, all_errors


def main():
    """Test the validator"""
    print("Testing Data Validator...")
    print("=" * 50)

    validator = DataValidator()

    # Test stock data
    test_stock = {
        'symbol': 'VCB',
        'name': 'Vietcombank',
        'sector': 'banking',
        'exchange': 'HOSE',
        'market_cap': 1000000000000
    }

    is_valid, errors = validator.validate_stock_data(test_stock)
    print(f"Stock validation: {'✓' if is_valid else '✗'} ({len(errors)} errors)")

    # Test price data
    test_price = {
        'stock_symbol': 'VCB',
        'date': '2024-01-15',
        'open': 85000,
        'high': 86000,
        'low': 84000,
        'close': 85500,
        'volume': 1000000
    }

    is_valid, errors = validator.validate_price_data(test_price)
    print(f"Price validation: {'✓' if is_valid else '✗'} ({len(errors)} errors)")

    if errors:
        for error in errors:
            print(f"  - {error}")


if __name__ == "__main__":
    main()