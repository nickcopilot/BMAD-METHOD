# Vietnam Stock Analysis System - Architecture Documentation

## Executive Summary

The Vietnam Stock Analysis System is a production-ready trading intelligence platform designed specifically for the Vietnamese stock market. The system implements a comprehensive end-to-end trading architecture that combines real-time data collection, advanced analytical algorithms, portfolio optimization, risk management, and automated trading signals.

### System Classification
- **Type**: Financial Trading Intelligence Platform
- **Market Focus**: Vietnamese Stock Market (HOSE, HNX, UPCOM)
- **Architecture Pattern**: Layered Service-Oriented Architecture
- **Deployment Model**: Single-node production system with web dashboard
- **Data Architecture**: SQLite-based with real-time processing capabilities

## System Overview

### Core Mission
Provide institutional-grade trading intelligence for Vietnamese stock market participants through advanced smart money analysis, Modern Portfolio Theory implementation, and real-time risk management capabilities.

### Key Capabilities
- **Data Collection**: Automated collection from VNStock API and Vietnamese economic indicators
- **Smart Money Analysis**: Vietnamese market-calibrated institutional behavior detection
- **Portfolio Optimization**: Modern Portfolio Theory with Vietnamese market constraints
- **Risk Management**: Dynamic position sizing with correlation-based controls
- **Trading Signals**: High-precision entry/exit signals with technical confluence
- **Strategy Backtesting**: Historical validation framework with performance attribution
- **Alert System**: Automated high-probability setup detection

## Architectural Layers

### 1. Data Collection Layer
**Purpose**: Reliable acquisition and normalization of Vietnamese market data

**Components**:
- **VNStock Collector** (`data_collection/vnstock_collector.py`)
  - Interfaces with vnstock Python library
  - Collects price, volume, and company data for 20 tracked stocks
  - Implements retry logic and error handling
  - Supports 4 sectors: Banking, Real Estate, Steel, Securities

- **GSO Economic Collector** (`data_collection/gso_collector.py`)
  - Collects Vietnamese economic indicators
  - Integrates with General Statistics Office data
  - Provides macroeconomic context for analysis

- **Data Scheduler** (`data_collection/scheduler.py`)
  - Orchestrates automated data collection
  - Manages collection schedules and error recovery
  - Provides monitoring and logging capabilities

**Data Flow**:
```
External APIs → Collectors → Validation → Database → Analysis Layer
```

### 2. Data Persistence Layer
**Purpose**: Centralized data storage with optimized access patterns

**Database Schema**:
- **stocks**: Master stock information with sector classification
- **price_data**: Time-series price and volume data with foreign key constraints
- **financial_data**: Company fundamental data (quarterly/annual)
- **economic_indicators**: Vietnamese macroeconomic data
- **eic_scores**: Economy-Industry-Company composite scores
- **portfolio**: User portfolio positions with entry tracking
- **alerts**: System-generated alerts with read status

**Key Features**:
- SQLite production database with proper indexing
- Compound primary keys for time-series data
- Foreign key constraints for data integrity
- Optimized indexes for performance-critical queries

### 3. Analysis Layer
**Purpose**: Advanced financial analysis with Vietnamese market specialization

**Smart Money Analyzer** (`shared/analysis/smart_money.py`):
- **Volume Pattern Analysis**: Stealth accumulation and institutional flow detection
- **Price Action Analysis**: Breakout signals and moving average alignment
- **Momentum Analysis**: RSI divergence and momentum persistence tracking
- **Accumulation/Distribution**: Smart money accumulation pattern detection
- **Vietnamese Market Context**: Sector-specific adjustments and local calibrations

**Signal Processing Pipeline**:
```
Raw Data → Technical Indicators → Component Analysis → Composite Scoring → Market Context → Actionable Signals
```

**Scoring System**:
- Weighted composite scoring (0-100 scale)
- Vietnamese market calibration factors
- Signal classification: Strong Buy/Buy/Weak Buy/Hold/Sell/Strong Sell
- Confidence levels and strength indicators

### 4. Trading Strategy Layer
**Purpose**: Professional-grade trading intelligence and execution planning

#### Portfolio Optimization Engine (`trading/portfolio_optimizer.py`)
- **Modern Portfolio Theory**: Risk-adjusted return optimization
- **Vietnamese Constraints**:
  - Max 15% position size, 40% sector allocation
  - Min 8 stocks diversification requirement
  - 5% cash reserve maintenance
- **Smart Money Integration**: Signal strength weighting in allocation
- **Transaction Cost Modeling**: 0.15% commission + market impact

#### Risk Management System (`trading/risk_manager.py`)
- **Dynamic Position Sizing**: ATR-based volatility adjustment
- **Correlation Controls**: 70% correlation threshold monitoring
- **Portfolio Risk Monitoring**: Max 20% annual volatility target
- **Stop-Loss Management**: 2x ATR dynamic stops
- **Sector Risk Limits**: Max 12% risk concentration per sector

#### Strategy Backtesting Framework (`trading/backtester.py`)
- **Historical Validation**: Performance testing with realistic costs
- **Trade Attribution**: Win/loss analysis by signal type
- **Risk-Adjusted Metrics**: Sharpe ratio, max drawdown, sortino ratio
- **Vietnamese Market Simulation**: Local market microstructure modeling

#### Real-Time Signal Generator (`trading/signal_generator.py`)
- **Entry/Exit Precision**: Support/resistance level calculation
- **Technical Confluence**: Multi-indicator confirmation scoring
- **Risk-Reward Analysis**: Position sizing recommendations
- **Timing Optimization**: Multi-timeframe validation

#### Automated Alert System (`trading/alert_system.py`)
- **High-Probability Detection**: 75% confidence threshold filtering
- **Smart Cooldown Management**: 4-hour symbol-specific cooldowns
- **Alert Types**: Strong Buy, Breakout, Risk Warning, Sector Rotation
- **Priority Management**: Risk-weighted alert prioritization

### 5. Presentation Layer
**Purpose**: Interactive web-based dashboard for system interaction

**Streamlit Dashboard** (`dashboard/main.py`):
- **Market Overview**: Real-time stock performance with sector filtering
- **Individual Analysis**: Detailed stock analysis with component breakdown
- **Smart Signals**: Signal history and current recommendations
- **Portfolio Tracker**: Position management with P&L calculation
- **Sector Analysis**: Cross-sector comparison and correlation analysis

**UI Architecture**:
- Component-based design with caching optimization
- Real-time data binding with 5-minute refresh cycles
- Interactive visualizations using Plotly
- Responsive design for multiple screen sizes

## Data Architecture

### Data Models

#### Core Entities
```python
@dataclass
class Stock:
    symbol: str           # Primary identifier
    name: str            # Vietnamese company name
    name_en: str         # English company name
    sector: str          # Sector classification
    exchange: str        # HOSE/HNX/UPCOM
    market_cap: float    # Market capitalization
    industry_group: str  # Industry classification
    listing_date: str    # IPO date
```

#### Time-Series Data
```python
@dataclass
class PriceData:
    stock_symbol: str    # Foreign key to stocks
    date: str           # Trading date (YYYY-MM-DD)
    open: float         # Opening price
    high: float         # Daily high
    low: float          # Daily low
    close: float        # Closing price
    volume: int         # Trading volume
    value: float        # Trading value
    foreign_buy: float  # Foreign buying volume
    foreign_sell: float # Foreign selling volume
```

### Data Flow Architecture

```
Data Sources → Collection → Validation → Storage → Analysis → Presentation
     ↓              ↓           ↓          ↓         ↓           ↓
VNStock API → vnstock_collector → validators → SQLite → smart_money → Dashboard
GSO Data   → gso_collector     → data_models → Indexes → portfolio_opt → Alerts
Economic   → scheduler         → integrity   → Backup  → risk_mgmt    → Reports
```

## System Integration Patterns

### Service Communication
- **Database-Centric**: All components communicate through centralized database
- **Event-Driven**: Alert system responds to data changes and threshold breaches
- **Batch Processing**: Data collection and analysis operate on scheduled intervals
- **Real-Time**: Dashboard provides live updates with caching optimization

### Error Handling Strategy
- **Graceful Degradation**: System continues operation with partial data
- **Retry Logic**: Exponential backoff for external API failures
- **Fallback Mechanisms**: Alternative data sources and calculation methods
- **Comprehensive Logging**: Structured logging for debugging and monitoring

### Performance Optimization
- **Database Indexing**: Optimized indexes for time-series queries
- **Caching Strategy**: Streamlit caching for expensive calculations
- **Lazy Loading**: On-demand data loading in dashboard components
- **Memory Management**: Efficient pandas operations with data cleanup

## Security Architecture

### Data Protection
- **Local Storage**: SQLite database with file-system level security
- **Input Validation**: Comprehensive data validation and sanitization
- **API Rate Limiting**: Respectful API usage with throttling
- **Error Isolation**: Exception handling prevents system-wide failures

### Access Control
- **File-System Security**: Standard Unix permissions
- **Network Security**: Local-only dashboard access by default
- **Data Integrity**: Foreign key constraints and validation rules

## Deployment Architecture

### Development Environment
- **Platform**: Linux-based (Ubuntu/CodeSpaces compatible)
- **Python Version**: 3.8+ with modern libraries
- **Dependencies**: Managed via requirements.txt
- **Development Tools**: Integrated testing and validation scripts

### Production Considerations
- **Scalability**: Single-node design optimized for Vietnamese market scope
- **Reliability**: Robust error handling and recovery mechanisms
- **Monitoring**: Comprehensive logging and health check capabilities
- **Backup**: Database backup and recovery procedures

## Quality Attributes

### Performance
- **Latency**: Sub-second dashboard response times
- **Throughput**: Handles 20 stocks with minute-level updates
- **Scalability**: Designed for Vietnamese market scope (extensible)
- **Efficiency**: Optimized algorithms with minimal resource usage

### Reliability
- **Availability**: 99%+ uptime with graceful error handling
- **Fault Tolerance**: Continues operation with partial data
- **Recovery**: Automatic restart and data integrity preservation
- **Monitoring**: Comprehensive logging and health metrics

### Maintainability
- **Modularity**: Clear separation of concerns across layers
- **Testability**: Comprehensive test suite with validation scripts
- **Documentation**: Complete API documentation and user guides
- **Code Quality**: Consistent styling and architectural patterns

### Security
- **Data Protection**: Local storage with access controls
- **Input Validation**: Comprehensive sanitization and validation
- **Error Handling**: Secure failure modes without information leakage

## Vietnamese Market Specializations

### Market Structure Adaptations
- **Trading Hours**: Vietnamese market schedule (9:00 AM - 3:00 PM local)
- **Settlement Cycles**: T+2 settlement for position tracking
- **Currency**: VND pricing with appropriate precision
- **Regulatory**: Vietnamese securities regulations compliance

### Calibration Parameters
- **Volatility Adjustment**: +20% factor for Vietnamese market characteristics
- **Risk-Free Rate**: 6% Vietnamese government bond yield
- **Transaction Costs**: 0.15% commission + 0.1% market impact
- **Position Limits**: 15% max position size, 40% max sector allocation
- **Correlation Thresholds**: 70% warning level for portfolio risk

### Cultural Trading Patterns
- **Sector Leadership**: Banking sector weight adjustment (1.25x)
- **Foreign Ownership**: Enhanced weighting for foreign-attractive stocks
- **State Ownership**: Reduced volatility factor (0.85x) for SOEs
- **Market Sentiment**: Vietnamese-specific sentiment indicators

## Future Architecture Considerations

### Scalability Enhancements
- **Multi-Market Support**: Extension to other Asian markets
- **Real-Time Processing**: Stream processing for tick-level data
- **Cloud Migration**: Containerization and cloud deployment
- **API Development**: RESTful API for external integrations

### Technology Evolution
- **Machine Learning**: Advanced pattern recognition and prediction
- **Microservices**: Service decomposition for better scalability
- **Real-Time Execution**: Automated trading system integration
- **Advanced Analytics**: Deep learning for market prediction

## Conclusion

The Vietnam Stock Analysis System represents a sophisticated financial technology platform specifically engineered for the Vietnamese market. The architecture successfully balances complexity with maintainability, providing institutional-grade capabilities while remaining accessible for individual traders and analysts.

The system's layered architecture, comprehensive error handling, and Vietnamese market specializations create a robust foundation for advanced trading intelligence. The modular design enables future enhancements while maintaining system stability and performance.

---

**Document Version**: 1.0
**Last Updated**: September 17, 2025
**Next Review**: December 17, 2025
**Architecture Status**: Production Ready