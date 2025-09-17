# Vietnam Stock Analysis System

A comprehensive stock analysis and portfolio tracking system for the Vietnamese stock market.

## Features

- **Data Collection**: Automated collection from VNStock and GSO (General Statistics Office)
- **Technical Analysis**: RSI, MACD, Bollinger Bands, Moving Averages
- **Smart Money Signals**: Advanced institutional behavior tracking and analysis
- **Portfolio Tracking**: Add positions, track P&L, sector allocation
- **Interactive Dashboard**: Streamlit-based web interface with Smart Signals
- **Market Overview**: Real-time stock data and performance metrics

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Dashboard

```bash
python run_dashboard.py
```

This will:
- Check dependencies
- Collect initial data if needed
- Launch the dashboard at http://localhost:8501

### 3. Access the Dashboard

- **Local**: Open http://localhost:8501 in your browser
- **Codespaces**: Use the 'Ports' tab and open port 8501

## Manual Operations

### Collect Data

```bash
# Test data collection
python test_collection.py

# Run scheduled data collection
python data_collection/scheduler.py --run-now daily_stock
```

### Test Portfolio

```bash
# Test portfolio functionality
python test_portfolio.py
```

### Run Scheduler

```bash
# Start automated data collection
python data_collection/scheduler.py
```

## Project Structure

```
vietnam-stock-analysis/
├── dashboard/                 # Streamlit dashboard
│   └── main.py               # Main dashboard application
├── data_collection/          # Data collection modules
│   ├── vnstock_collector.py  # Vietnamese stock data
│   ├── gso_collector.py      # Economic indicators
│   └── scheduler.py          # Automated scheduling
├── shared/                   # Shared utilities
│   ├── models/              # Database models
│   └── utils/               # Utilities and validators
├── data/                    # Database storage
│   └── vietnam_stocks.db    # SQLite database
├── tests/                   # Test files
├── config/                  # Configuration files
└── docs/                    # Documentation
```

## Database Schema

- **stocks**: Stock information (symbol, name, sector, exchange)
- **price_data**: Daily price and volume data
- **portfolio**: User portfolio positions
- **financial_data**: Company financial reports
- **economic_indicators**: Vietnamese economic data
- **eic_scores**: Economy-Industry-Company scores
- **alerts**: Price and indicator alerts

## Dashboard Pages

1. **Market Overview**: Available stocks and recent performance
2. **Stock Analysis**: Individual stock analysis with technical indicators
3. **Smart Signals**: Advanced smart money analysis and institutional behavior tracking
4. **Portfolio Tracker**: Portfolio management and performance tracking
5. **Economic Indicators**: Vietnamese economic data (when available)

## Portfolio Features

- Add/remove positions
- Real-time P&L calculation
- Sector allocation analysis
- Performance metrics
- Position management

## Technical Indicators

- **Moving Averages**: 5, 10, 20-day
- **RSI**: Relative Strength Index (14-day)
- **MACD**: Moving Average Convergence Divergence
- **Bollinger Bands**: 20-day with 2 standard deviations

## Smart Money Features

- **Volume Analysis**: Stealth accumulation and institutional flow detection
- **Price Action**: Breakout signals and moving average alignment
- **Momentum**: RSI divergence and momentum persistence tracking
- **Accumulation/Distribution**: Smart money accumulation pattern detection
- **Market Context**: Vietnamese market-specific adjustments and sector analysis
- **Entry/Exit Signals**: Precise levels with risk management parameters
- **Composite Scoring**: Weighted signal strength with actionable recommendations

## Data Sources

- **VNStock**: Vietnamese stock market data
- **GSO**: Vietnam General Statistics Office economic indicators

## Configuration

Edit `config/` files to customize:
- Data collection schedules
- Technical indicator parameters
- Dashboard settings

## Development

### Adding New Indicators

1. Add calculation logic to `dashboard/main.py`
2. Update chart display functions
3. Test with sample data

### Adding New Data Sources

1. Create collector in `data_collection/`
2. Add database schema if needed
3. Update scheduler configuration

### Testing

```bash
# Test all functionality
python test_collection.py
python test_portfolio.py

# Run specific tests
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Missing dependencies**: Run `pip install -r requirements.txt`
2. **Database not found**: Run `python test_collection.py` to collect initial data
3. **Port 8501 busy**: Change port in `run_dashboard.py`

### Database Reset

```bash
# Remove database to start fresh
rm data/vietnam_stocks.db

# Collect new data
python test_collection.py
```

## License

This project is for educational and research purposes.