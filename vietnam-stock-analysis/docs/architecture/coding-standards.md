# Vietnam Stock Analysis System - Coding Standards

## Overview

This document defines the coding standards and best practices for the Vietnam Stock Analysis System. These standards ensure code consistency, maintainability, and reliability across the codebase while reflecting the existing architectural patterns discovered in the production system.

## General Principles

### Code Philosophy
1. **Clarity over Cleverness**: Write code that is easily understood by future developers
2. **Vietnamese Market Focus**: Code should reflect Vietnamese market specifics and constraints
3. **Production Ready**: All code must include proper error handling and logging
4. **Modular Design**: Components should be loosely coupled and highly cohesive
5. **Data Integrity**: Financial data accuracy is paramount - validate everything

### Architecture Alignment
- Follow the established layered architecture pattern
- Maintain separation between data collection, analysis, trading strategy, and presentation layers
- Use dependency injection for database connections
- Implement consistent error handling patterns across all modules

## Python Coding Standards

### Code Style
Follow PEP 8 with specific adaptations for financial systems:

```python
# File header template for all modules
#!/usr/bin/env python3
"""
Module Name - Brief Description
Purpose and scope description
"""

import standard_library_modules
import third_party_modules
import sys
import os

# Add project modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from local_modules
```

### Naming Conventions

#### Variables and Functions
```python
# Use snake_case for variables and functions
stock_symbol = "VCB"
price_data = get_price_data(symbol, days_back=30)
smart_money_score = calculate_composite_score()

# Vietnamese market specific naming
vn_market_adjustment = 1.2
hose_exchange_data = collect_hose_data()
vnd_price_precision = 1000  # Vietnamese Dong pricing
```

#### Classes
```python
# Use PascalCase for classes
class VNStockCollector:
    """Collects data from Vietnamese stock exchanges"""

class SmartMoneyAnalyzer:
    """Analyzes institutional behavior in Vietnamese market"""

class VietnamesePortfolioOptimizer:
    """Modern Portfolio Theory with Vietnamese constraints"""
```

#### Constants
```python
# Use UPPER_SNAKE_CASE for constants
MAX_POSITION_SIZE = 0.15        # 15% maximum position
VN_RISK_FREE_RATE = 0.06        # Vietnamese government bonds
HOSE_TRADING_HOURS = (9, 15)    # 9 AM to 3 PM local time
TRANSACTION_COST_VN = 0.0015    # 0.15% Vietnamese brokerage
```

### Data Models and Type Hints

#### Database Models
```python
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from enum import Enum

@dataclass
class Stock:
    """Stock information model following database schema"""
    symbol: str
    name: str
    name_en: str
    sector: str
    exchange: str
    market_cap: float
    industry_group: str
    listing_date: str
    is_active: bool = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

# Use Enums for Vietnamese market constants
class Sector(Enum):
    SECURITIES = "securities"
    BANKING = "banking"
    REAL_ESTATE = "real_estate"
    STEEL = "steel"

class Exchange(Enum):
    HOSE = "HOSE"  # Ho Chi Minh Stock Exchange
    HNX = "HNX"    # Hanoi Stock Exchange
    UPCOM = "UPCOM" # Unlisted Public Company Market
```

#### Function Signatures
```python
def calculate_smart_money_score(
    symbol: str,
    days_back: int = 60,
    market_context: bool = True
) -> Dict[str, Any]:
    """
    Calculate smart money score for Vietnamese stock

    Args:
        symbol: Stock symbol (e.g., 'VCB', 'HPG')
        days_back: Number of days for analysis
        market_context: Apply Vietnamese market adjustments

    Returns:
        Dictionary containing scores and analysis

    Raises:
        ValueError: If symbol not found or invalid days_back
        DatabaseError: If unable to fetch price data
    """
```

### Error Handling Standards

#### Exception Patterns
```python
import logging

logger = logging.getLogger(__name__)

def robust_data_collection(symbol: str) -> Optional[Dict]:
    """Example of production-ready error handling"""
    try:
        # Attempt primary data source
        data = primary_api_call(symbol)

        if not data:
            logger.warning(f"No data from primary source for {symbol}")
            # Attempt fallback
            data = fallback_data_source(symbol)

        return validate_and_clean_data(data)

    except APIRateLimitError:
        logger.error(f"Rate limit exceeded for {symbol}")
        # Implement exponential backoff
        return None

    except DataValidationError as e:
        logger.error(f"Data validation failed for {symbol}: {e}")
        return None

    except Exception as e:
        logger.error(f"Unexpected error collecting {symbol}: {e}")
        # Never let exceptions bubble up unhandled
        return None
```

#### Vietnamese Market Specific Error Handling
```python
class VietnameseMarketError(Exception):
    """Base exception for Vietnamese market specific errors"""
    pass

class VNStockAPIError(VietnameseMarketError):
    """VNStock API specific errors"""
    pass

class VNMarketHoursError(VietnameseMarketError):
    """Trading hours validation errors"""
    pass

def validate_vn_trading_hours(timestamp: datetime) -> bool:
    """Validate if timestamp is within Vietnamese trading hours"""
    if not is_vn_trading_day(timestamp):
        raise VNMarketHoursError(f"Non-trading day: {timestamp.date()}")

    hour = timestamp.hour
    if not (9 <= hour < 15):  # 9 AM to 3 PM
        raise VNMarketHoursError(f"Outside trading hours: {hour}:00")

    return True
```

### Database Interaction Standards

#### Database Access Patterns
```python
class DatabaseManager:
    """Follow existing database patterns"""

    def __init__(self, db_path: str = "data/vietnam_stocks.db"):
        self.db_path = db_path
        # Always ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Standard connection pattern with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def safe_insert(self, table: str, data: Dict) -> bool:
        """Safe insertion with error handling"""
        try:
            with self.get_connection() as conn:
                placeholders = ', '.join(['?' for _ in data.values()])
                columns = ', '.join(data.keys())

                conn.execute(
                    f"INSERT OR REPLACE INTO {table} ({columns}) VALUES ({placeholders})",
                    list(data.values())
                )
                conn.commit()
                return True

        except sqlite3.Error as e:
            logger.error(f"Database insertion failed: {e}")
            return False
```

#### Query Patterns
```python
def get_vn_market_data(self, symbol: str, days_back: int) -> List[Dict]:
    """Standard query pattern for Vietnamese market data"""
    with self.get_connection() as conn:
        cursor = conn.execute("""
            SELECT pd.*, s.sector, s.name
            FROM price_data pd
            JOIN stocks s ON pd.stock_symbol = s.symbol
            WHERE pd.stock_symbol = ?
            AND pd.date >= date('now', '-{} days')
            ORDER BY pd.date DESC
        """.format(days_back), (symbol,))

        return [dict(row) for row in cursor.fetchall()]
```

### Analysis and Trading Module Standards

#### Signal Generation Patterns
```python
class SignalGenerator:
    """Standard pattern for Vietnamese market signal generation"""

    def __init__(self):
        # Vietnamese market calibration parameters
        self.vn_config = {
            'volatility_adjustment': 1.2,  # +20% for VN market
            'min_volume_threshold': 100000,  # VND value
            'sector_weights': {
                'banking': 1.25,      # Banking leadership
                'securities': 1.15,
                'real_estate': 1.0,
                'steel': 0.95
            }
        }

    def generate_signals(self, symbol: str) -> Dict[str, Any]:
        """
        Generate trading signals with Vietnamese market context

        Returns structured signal data following established patterns
        """
        try:
            # Follow established analysis pipeline
            data = self._load_symbol_data(symbol)
            technical_scores = self._calculate_technical_signals(data)
            vn_context = self._apply_vietnamese_context(symbol, technical_scores)

            return {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'composite_score': self._calculate_composite(technical_scores, vn_context),
                'signal_components': technical_scores,
                'vn_market_context': vn_context,
                'recommended_action': self._generate_recommendation(technical_scores)
            }

        except Exception as e:
            logger.error(f"Signal generation failed for {symbol}: {e}")
            return self._generate_neutral_signal(symbol)
```

#### Risk Management Patterns
```python
def calculate_vn_position_size(
    signal_strength: float,
    portfolio_value: float,
    stock_volatility: float,
    sector: str
) -> float:
    """Vietnamese market position sizing with local constraints"""

    # Base position size (1-5% of portfolio)
    base_size = min(0.05, max(0.01, signal_strength / 100 * 0.05))

    # Vietnamese market adjustments
    vn_adjustments = {
        'banking': 1.1,        # Higher allocation for banking leaders
        'securities': 1.0,
        'real_estate': 0.9,    # More volatile sector
        'steel': 0.85          # Cyclical sector caution
    }

    # Volatility adjustment
    vol_adjustment = max(0.5, min(1.5, 1.0 / (stock_volatility * 2)))

    # Apply Vietnamese constraints
    max_position = 0.15  # 15% maximum position size
    position_size = base_size * vn_adjustments.get(sector, 1.0) * vol_adjustment

    return min(position_size, max_position) * portfolio_value
```

### Testing Standards

#### Unit Test Patterns
```python
import pytest
import pandas as pd
from unittest.mock import Mock, patch

class TestVietnameseMarketAnalysis:
    """Test class following established patterns"""

    @pytest.fixture
    def sample_vn_data(self):
        """Sample Vietnamese market data for testing"""
        return pd.DataFrame({
            'symbol': ['VCB', 'HPG', 'VHM'],
            'close': [85000, 25000, 75000],  # VND prices
            'volume': [1000000, 2000000, 1500000],
            'date': pd.date_range('2024-01-01', periods=3)
        })

    def test_smart_money_analysis_vn_calibration(self, sample_vn_data):
        """Test Vietnamese market calibration in smart money analysis"""
        analyzer = SmartMoneyAnalyzer()

        # Test with Vietnamese banking stock
        result = analyzer.analyze_symbol('VCB', days_back=30)

        # Verify Vietnamese market adjustments applied
        assert 'vn_market_context' in result
        assert result['vn_market_context']['banking_sector'] is True
        assert result['vn_market_context']['adjustment_factor'] >= 1.0

    @patch('vnstock.Quote')
    def test_data_collection_resilience(self, mock_vnstock):
        """Test data collection error handling"""
        # Simulate API failure
        mock_vnstock.side_effect = Exception("API Error")

        collector = VNStockCollector()
        result = collector.collect_stock_info('VCB')

        # Should handle gracefully, not raise exception
        assert result is None or isinstance(result, dict)
```

### Documentation Standards

#### Docstring Format
```python
def optimize_vn_portfolio(
    symbols: List[str],
    risk_tolerance: float,
    sector_limits: Dict[str, float]
) -> Dict[str, Any]:
    """
    Optimize portfolio allocation for Vietnamese market constraints.

    Implements Modern Portfolio Theory with Vietnamese market specific
    constraints including sector allocation limits, transaction costs,
    and regulatory position size limits.

    Args:
        symbols: List of Vietnamese stock symbols (e.g., ['VCB', 'HPG'])
        risk_tolerance: Portfolio volatility target (0.15 = 15% annual)
        sector_limits: Max allocation per sector {'banking': 0.4, 'steel': 0.3}

    Returns:
        Dictionary containing:
            - optimal_weights: Dict[str, float] - Symbol to weight mapping
            - expected_return: float - Annual expected return
            - portfolio_risk: float - Annual portfolio volatility
            - sharpe_ratio: float - Risk-adjusted return metric
            - vn_constraints_met: bool - Vietnamese regulatory compliance

    Raises:
        PortfolioOptimizationError: If optimization fails to converge
        InsufficientDataError: If not enough price history available
        VNRegulatoryError: If constraints cannot be satisfied

    Example:
        >>> optimizer = VietnamesePortfolioOptimizer()
        >>> result = optimizer.optimize_vn_portfolio(
        ...     symbols=['VCB', 'HPG', 'VHM'],
        ...     risk_tolerance=0.18,
        ...     sector_limits={'banking': 0.4, 'steel': 0.3, 'real_estate': 0.3}
        ... )
        >>> print(f"Optimal VCB weight: {result['optimal_weights']['VCB']:.2%}")
    """
```

#### Module Documentation
```python
"""
Vietnamese Portfolio Optimization Engine

This module implements Modern Portfolio Theory specifically adapted for
the Vietnamese stock market. Key adaptations include:

- Vietnamese regulatory position limits (15% max per stock)
- Sector concentration limits (40% max per sector)
- Vietnamese transaction cost modeling (0.15% commission)
- Local market volatility adjustments (+20% factor)
- Vietnamese risk-free rate (6% government bonds)

The optimization engine integrates with the Smart Money Analyzer to
incorporate institutional behavior signals into allocation decisions.

Classes:
    VietnamesePortfolioOptimizer: Main optimization engine
    VNMarketConstraints: Vietnamese regulatory constraints
    VNRiskModel: Vietnamese market risk modeling

Usage:
    from trading.portfolio_optimizer import VietnamesePortfolioOptimizer

    optimizer = VietnamesePortfolioOptimizer()
    portfolio = optimizer.optimize_portfolio()

See Also:
    smart_money.py: Signal generation for optimization inputs
    risk_manager.py: Portfolio risk monitoring

Author: Vietnam Stock Analysis System
Created: September 2025
"""
```

### Performance Standards

#### Optimization Guidelines
```python
# Use pandas efficiently for Vietnamese market data
def efficient_vn_data_processing(df: pd.DataFrame) -> pd.DataFrame:
    """Follow performance best practices for Vietnamese market data"""

    # Use vectorized operations instead of loops
    df['vnd_adjusted'] = df['close'] * 1000  # Convert to proper VND
    df['volume_vnd'] = df['volume'] * df['close']

    # Use .loc for data selection
    banking_stocks = df.loc[df['sector'] == 'banking'].copy()

    # Chain operations efficiently
    result = (df
              .groupby('sector')
              .agg({
                  'close': 'mean',
                  'volume': 'sum',
                  'market_cap': 'sum'
              })
              .round(2))

    return result

# Cache expensive calculations
@functools.lru_cache(maxsize=128)
def calculate_correlation_matrix(symbols_tuple: Tuple[str, ...]) -> np.ndarray:
    """Cache correlation calculations for Vietnamese stocks"""
    # Convert tuple back to list for processing
    symbols = list(symbols_tuple)
    # Expensive correlation calculation here
    return correlation_matrix
```

### Logging Standards

#### Logging Configuration
```python
import logging
from datetime import datetime

# Standard logging setup for all modules
def setup_vn_market_logging(module_name: str) -> logging.Logger:
    """Setup consistent logging for Vietnamese market modules"""

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(f'logs/vn_market_{datetime.now():%Y%m%d}.log'),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(module_name)
    return logger

# Usage in modules
logger = setup_vn_market_logging(__name__)

# Standard logging patterns
def collect_vn_stock_data(symbol: str):
    """Example of proper logging in Vietnamese market context"""

    logger.info(f"Starting data collection for Vietnamese stock: {symbol}")

    try:
        data = fetch_vnstock_data(symbol)
        logger.info(f"Successfully collected {len(data)} records for {symbol}")

    except VNStockAPIError as e:
        logger.error(f"VNStock API error for {symbol}: {e}")

    except Exception as e:
        logger.error(f"Unexpected error collecting {symbol}: {e}", exc_info=True)
```

## Vietnamese Market Specific Standards

### Currency and Precision
```python
# Vietnamese Dong handling
VND_PRECISION = 1000  # Round to nearest 1000 VND
VND_DISPLAY_FACTOR = 1000  # Display in thousands

def format_vnd_price(price: float) -> str:
    """Format Vietnamese Dong for display"""
    return f"{price/1000:,.0f}K VND"

def validate_vnd_price(price: float) -> bool:
    """Validate Vietnamese Dong price precision"""
    return price % VND_PRECISION == 0
```

### Market Hours and Calendar
```python
from datetime import datetime, time
import holidays

def is_vn_trading_day(date: datetime) -> bool:
    """Check if date is Vietnamese trading day"""
    vietnam_holidays = holidays.Vietnam()

    # Weekend check
    if date.weekday() >= 5:  # Saturday = 5, Sunday = 6
        return False

    # Holiday check
    if date.date() in vietnam_holidays:
        return False

    return True

VN_MARKET_OPEN = time(9, 0)   # 9:00 AM
VN_MARKET_CLOSE = time(15, 0) # 3:00 PM

def get_vn_trading_session(dt: datetime) -> str:
    """Determine Vietnamese market session"""
    if time(9, 0) <= dt.time() < time(11, 30):
        return "morning"
    elif time(13, 0) <= dt.time() < time(15, 0):
        return "afternoon"
    else:
        return "closed"
```

### Regulatory Compliance
```python
# Vietnamese Securities Law compliance
VN_MAX_POSITION_SIZE = 0.15      # 15% maximum position
VN_MAX_SECTOR_ALLOCATION = 0.40  # 40% maximum sector allocation
VN_MIN_DIVERSIFICATION = 8       # Minimum 8 stocks
VN_FOREIGN_OWNERSHIP_LIMIT = 0.49 # 49% foreign ownership limit

def validate_vn_portfolio_compliance(weights: Dict[str, float]) -> bool:
    """Validate portfolio against Vietnamese regulations"""

    # Check position size limits
    for symbol, weight in weights.items():
        if weight > VN_MAX_POSITION_SIZE:
            raise VNRegulatoryError(f"Position {symbol} exceeds 15% limit: {weight:.1%}")

    # Check diversification requirement
    active_positions = sum(1 for w in weights.values() if w > 0.01)
    if active_positions < VN_MIN_DIVERSIFICATION:
        raise VNRegulatoryError(f"Need minimum {VN_MIN_DIVERSIFICATION} positions")

    return True
```

## Code Review Standards

### Review Checklist
1. **Vietnamese Market Accuracy**: Verify all Vietnamese market parameters are correct
2. **Error Handling**: Ensure robust error handling for API failures and data issues
3. **Performance**: Check for efficient pandas operations and database queries
4. **Testing**: Verify comprehensive test coverage for Vietnamese market scenarios
5. **Documentation**: Ensure Vietnamese market context is properly documented
6. **Logging**: Confirm appropriate logging for troubleshooting
7. **Compliance**: Verify Vietnamese regulatory constraints are enforced

### Common Patterns to Enforce
- Always use the established database connection patterns
- Include Vietnamese market context in all analysis functions
- Follow the existing error handling and logging patterns
- Use type hints for all public functions
- Include docstrings with Vietnamese market context
- Test with realistic Vietnamese market data

## File Organization Standards

### Module Structure
```
module_name.py
├── Module docstring with Vietnamese context
├── Imports (standard → third-party → local)
├── Constants (Vietnamese market parameters)
├── Helper functions
├── Main classes
├── Public API functions
└── Main execution block (if applicable)
```

### Directory Structure
```
vietnam-stock-analysis/
├── shared/           # Shared utilities and models
├── data_collection/  # Data collection modules
├── trading/          # Trading strategy modules
├── dashboard/        # Web interface
├── docs/            # Documentation
├── tests/           # Test modules
└── data/            # Database and data files
```

---

**Document Version**: 1.0
**Last Updated**: September 17, 2025
**Review Cycle**: Monthly
**Compliance**: Vietnamese Securities Law, BMAD Framework