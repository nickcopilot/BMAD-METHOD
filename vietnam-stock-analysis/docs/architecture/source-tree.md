# Vietnam Stock Analysis System - Source Tree Documentation

## Overview

This document provides a comprehensive guide to the source code organization and file structure of the Vietnam Stock Analysis System. The project follows a layered architecture with clear separation of concerns and Vietnamese market-specific implementations.

## Root Directory Structure

```
vietnam-stock-analysis/
├── README.md                    # Project overview and quick start guide
├── SYSTEM_STATUS.md             # Complete system status and capabilities
├── requirements.txt             # Python dependencies with pinned versions
├── run_dashboard.py             # Main entry point for the web dashboard
├── data/                        # Database and data storage
├── shared/                      # Common utilities and models
├── data_collection/            # Data collection modules
├── trading/                    # Trading strategy engine
├── dashboard/                  # Web interface and visualization
├── docs/                       # Architecture and API documentation
├── tests/                      # Test files and validation scripts
├── config/                     # Configuration files
└── [Development Scripts]       # Various development and testing scripts
```

## Core Application Modules

### Shared Infrastructure (`shared/`)
**Purpose**: Common utilities, models, and infrastructure used across all modules

```
shared/
├── models/
│   ├── __init__.py
│   └── database.py             # Core database models and manager
├── analysis/
│   ├── __pycache__/
│   └── smart_money.py          # Vietnamese market-calibrated smart money analysis
└── utils/
    ├── __init__.py
    ├── __pycache__/
    └── validators.py           # Data validation utilities
```

#### Key Files Analysis:

**`shared/models/database.py`** (586 lines)
- **Purpose**: Complete database abstraction layer with Vietnamese market schema
- **Key Classes**:
  - `DatabaseManager`: Primary database interface with connection management
  - `Stock`, `PriceData`, `FinancialData`: Core data models using dataclasses
  - `EICScore`, `Portfolio`, `Alert`: Analysis and trading models
- **Key Features**:
  - SQLite database with production-ready schema
  - Portfolio tracking with P&L calculation
  - Vietnamese market-specific enums (Sector, Exchange, Recommendation)
  - Comprehensive CRUD operations with error handling
  - Database initialization with proper indexing

**`shared/analysis/smart_money.py`** (727 lines)
- **Purpose**: Advanced institutional behavior analysis for Vietnamese market
- **Key Class**: `SmartMoneyAnalyzer`
- **Analysis Components**:
  - Volume pattern analysis with stealth accumulation detection
  - Price action analysis with breakout detection
  - Momentum analysis with RSI and MACD integration
  - Accumulation/distribution pattern recognition
  - Vietnamese market context application
- **Key Features**:
  - Vietnamese market calibration factors
  - Composite scoring system (0-100 scale)
  - Signal classification: Strong Buy/Buy/Weak Buy/Hold/Sell/Strong Sell
  - Market overview with sector analysis

**`shared/utils/validators.py`**
- **Purpose**: Data validation and integrity checking
- **Functions**: Input validation, data consistency checks, market data validation

### Data Collection Layer (`data_collection/`)
**Purpose**: Automated collection from Vietnamese market data sources

```
data_collection/
├── __init__.py
├── __pycache__/               # Python bytecode cache
├── data/                      # Local data storage for collection module
│   └── vietnam_stocks.db     # Backup database instance
├── vnstock_collector.py       # Primary Vietnamese stock data collector
├── gso_collector.py          # Vietnamese economic indicators collector
└── scheduler.py              # Automated data collection scheduling
```

#### Key Files Analysis:

**`data_collection/vnstock_collector.py`** (100+ lines analyzed)
- **Purpose**: Primary data collection from VNStock API
- **Key Class**: `VNStockCollector`
- **Features**:
  - 20 Vietnamese stocks across 4 sectors (Banking, Real Estate, Steel, Securities)
  - Company information and price data collection
  - Sector mapping and classification
  - Error handling and retry logic
  - Integration with database models

**`data_collection/gso_collector.py`**
- **Purpose**: Vietnamese economic indicators from General Statistics Office
- **Features**: Web scraping for macroeconomic data, government statistics integration

**`data_collection/scheduler.py`**
- **Purpose**: Automated data collection orchestration
- **Features**: APScheduler integration, market hours awareness, error recovery

### Trading Strategy Engine (`trading/`)
**Purpose**: Professional-grade trading intelligence and portfolio management

```
trading/
├── __pycache__/               # Python bytecode cache
├── portfolio_optimizer.py     # Modern Portfolio Theory with Vietnamese constraints
├── risk_manager.py           # Advanced risk management system
├── backtester.py            # Strategy backtesting framework
├── signal_generator.py       # Real-time trading signals
└── alert_system.py          # Automated alert system
```

#### Key Files Analysis:

**`trading/portfolio_optimizer.py`** (415 lines)
- **Purpose**: Modern Portfolio Theory implementation for Vietnamese market
- **Key Class**: `VietnamesePortfolioOptimizer`
- **Features**:
  - Vietnamese market constraints (15% max position, 40% max sector)
  - Smart money signal integration for allocation weighting
  - Scipy optimization with SLSQP method
  - Transaction cost modeling (0.15% commission)
  - Risk-adjusted return optimization with Sharpe ratio maximization
  - Comprehensive portfolio reporting with sector allocation

**`trading/risk_manager.py`**
- **Purpose**: Dynamic risk management with Vietnamese market parameters
- **Features**: Position sizing, correlation monitoring, stop-loss management

**`trading/backtester.py`**
- **Purpose**: Historical strategy validation framework
- **Features**: Performance attribution, risk-adjusted metrics, Vietnamese market simulation

**`trading/signal_generator.py`**
- **Purpose**: Real-time trading signal generation
- **Features**: Multi-timeframe confluence, precision entry/exit levels

**`trading/alert_system.py`**
- **Purpose**: Automated high-probability setup detection
- **Features**: Smart filtering, cooldown management, risk warnings

### Dashboard Layer (`dashboard/`)
**Purpose**: Interactive web interface for market analysis and portfolio management

```
dashboard/
└── main.py                   # Complete Streamlit dashboard application
```

#### Key Files Analysis:

**`dashboard/main.py`** (100+ lines analyzed)
- **Purpose**: Complete web dashboard with Vietnamese market specialization
- **Features**:
  - Market overview with sector filtering
  - Individual stock analysis with technical indicators
  - Smart money signal visualization
  - Portfolio tracking with P&L calculation
  - Sector comparison and correlation analysis
- **Technical Implementation**:
  - Streamlit framework with caching optimization
  - Plotly visualizations for financial charts
  - Real-time data binding with 5-minute refresh cycles
  - Component-based architecture with modular functions

### Data Storage (`data/`)
**Purpose**: Database files and data persistence

```
data/
├── vietnam_stocks.db                              # Primary production database
├── vietnam_stocks_backup_20250917_072948.db      # Automated backup
└── alert_history.json                            # Alert system persistence
```

#### Database Schema:
- **stocks**: 20 Vietnamese stocks with sector classification
- **price_data**: Time-series price and volume data (1,449 records)
- **portfolio**: User portfolio positions with entry tracking
- **financial_data**: Company fundamental data
- **economic_indicators**: Vietnamese economic data
- **eic_scores**: Economy-Industry-Company composite scores
- **alerts**: System-generated alerts with status tracking

### Documentation (`docs/`)
**Purpose**: Comprehensive system documentation following BMAD standards

```
docs/
├── architecture.md                    # Main architecture documentation
└── architecture/
    ├── coding-standards.md           # Development standards and patterns
    ├── tech-stack.md                # Technology stack and dependencies
    └── source-tree.md               # This file - source code organization
```

### Configuration (`config/`)
**Purpose**: System configuration and parameter management

```
config/
└── [Configuration files for market parameters and system settings]
```

## Development and Testing Scripts

### Primary Development Scripts

**`run_dashboard.py`**
- **Purpose**: Main entry point for the web dashboard
- **Features**: Dependency checking, initial data collection, Streamlit launcher

**`test_collection.py`**
- **Purpose**: Data collection testing and validation
- **Features**: VNStock API testing, database population verification

**`test_portfolio.py`**
- **Purpose**: Portfolio functionality testing
- **Features**: Portfolio optimization testing, position management validation

**`test_smart_money.py`**
- **Purpose**: Smart money analysis validation
- **Features**: Signal generation testing, Vietnamese market calibration verification

**`test_calibrated_signals.py`**
- **Purpose**: Signal quality and calibration testing
- **Features**: Signal diversity analysis, Vietnamese market parameter validation

### System Enhancement Scripts

**`enhance_data_collection.py`**
- **Purpose**: Data collection system improvements
- **Features**: Enhanced data validation, error handling improvements

**`expand_stock_universe.py`**
- **Purpose**: Stock universe expansion to 20 stocks
- **Features**: Multi-sector expansion, database schema updates

**`fix_database_dates.py`**
- **Purpose**: Database date format standardization
- **Features**: Date format consistency, data integrity fixes

**`analyze_signal_correlation.py`**
- **Purpose**: Cross-stock correlation analysis
- **Features**: Signal correlation measurement, market relationship analysis

## File Organization Principles

### Layer Separation
1. **Data Layer**: `shared/models/` - Database models and data structures
2. **Business Logic**: `shared/analysis/`, `trading/` - Core analysis and trading logic
3. **Data Access**: `data_collection/` - External data source integration
4. **Presentation**: `dashboard/` - User interface and visualization
5. **Infrastructure**: `shared/utils/` - Common utilities and helpers

### Vietnamese Market Specialization
- All modules include Vietnamese market-specific calibrations
- Currency handling in Vietnamese Dong (VND) with proper precision
- Trading hours and calendar aligned with Vietnamese market schedule
- Regulatory constraints embedded throughout the system

### Code Organization Patterns

#### Module Structure Pattern
```python
module_name.py
├── Imports (standard → third-party → local)
├── Constants and configuration
├── Main class definitions
├── Helper functions
├── Vietnamese market calibrations
└── Main execution block (if standalone)
```

#### Class Organization Pattern
```python
class VietnameseMarketClass:
    def __init__(self):
        # Vietnamese market parameters
        self.vn_config = {...}

    def public_methods(self):
        # Main API functions
        pass

    def _private_methods(self):
        # Internal implementation
        pass

    def _vietnamese_market_methods(self):
        # Market-specific calibrations
        pass
```

### Database Integration Pattern
- All modules use centralized `DatabaseManager` from `shared/models/database.py`
- Consistent connection management with context managers
- Standardized error handling and logging
- Vietnamese market-specific table schema and relationships

### Error Handling Pattern
- Graceful degradation with partial functionality
- Comprehensive logging for debugging and monitoring
- Vietnamese market-specific error types and handling
- Production-ready exception management

## Build and Deployment Structure

### Dependencies Management
- **`requirements.txt`**: Pinned versions for production stability
- **Virtual Environment**: Recommended for development isolation
- **Python 3.8+**: Minimum version requirement

### Entry Points
1. **Web Dashboard**: `python run_dashboard.py`
2. **Data Collection**: `python test_collection.py`
3. **Portfolio Testing**: `python test_portfolio.py`
4. **Trading Modules**: Direct execution from `trading/` directory

### Configuration Management
- Environment-specific settings in `config/` directory
- Vietnamese market parameters embedded in code constants
- Database configuration in `DatabaseManager` constructor

## Development Workflow

### Adding New Features
1. **Analysis Features**: Add to `shared/analysis/` with Vietnamese calibration
2. **Trading Features**: Add to `trading/` with risk management integration
3. **Data Sources**: Add to `data_collection/` with error handling
4. **UI Features**: Add to `dashboard/main.py` with caching optimization

### Testing Strategy
- **Unit Tests**: Individual module testing in `tests/` directory
- **Integration Tests**: End-to-end testing with development scripts
- **Market Simulation**: Historical data testing with Vietnamese market parameters
- **Performance Testing**: Dashboard responsiveness and database query optimization

### Code Quality
- **Type Hints**: Comprehensive type annotations for public APIs
- **Documentation**: Docstrings with Vietnamese market context
- **Error Handling**: Production-ready exception management
- **Logging**: Structured logging for debugging and monitoring

## Performance Considerations

### Database Optimization
- **Indexing**: Compound indexes on (symbol, date) for time-series queries
- **Query Patterns**: Efficient JOIN operations for multi-table queries
- **Connection Management**: Connection pooling with context managers

### Memory Management
- **Pandas Optimization**: Efficient data types and chunked processing
- **Caching**: Streamlit caching for expensive calculations
- **Garbage Collection**: Explicit cleanup after large operations

### Vietnamese Market Specific Optimizations
- **Currency Precision**: Optimized VND handling with minimal memory overhead
- **Trading Hours**: Efficient time-based filtering for Vietnamese market sessions
- **Sector Analysis**: Optimized grouping operations for 4-sector classification

## Security and Data Protection

### Data Security
- **Local Storage**: SQLite database with file system security
- **Input Validation**: Comprehensive data sanitization in `shared/utils/validators.py`
- **Error Information**: Secure error handling without sensitive data leakage

### Access Control
- **Database Access**: Centralized through `DatabaseManager` with proper authorization
- **Web Interface**: Local-only access by default with configurable binding
- **API Integration**: Rate limiting and respectful usage of external APIs

---

**Document Version**: 1.0
**Last Updated**: September 17, 2025
**Total Source Files**: 20+ Python modules
**Total Lines of Code**: 2,000+ lines
**Architecture Maturity**: Production Ready