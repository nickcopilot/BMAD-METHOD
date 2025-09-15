# Vietnam Stock Analysis System

A comprehensive stock analysis platform for Vietnamese stocks featuring smart money tracking, EIC framework analysis, and market maker behavior detection.

## 🚀 Features

### Core Analysis Systems
- **📊 Comprehensive Stock Reports**: Deep analysis combining technical, fundamental, and market structure factors
- **🎯 Smart Money Signal System**: Advanced indicators tracking institutional money flow and entry/exit signals
- **🏢 EIC Framework**: Environment-Infrastructure-Competitiveness top-down analysis
- **💹 Market Maker Analysis**: Behavioral pattern analysis of market makers and liquidity providers
- **🌏 Stock Universe Manager**: Liquid stock discovery with penny stock and low-liquidity filtering

### Key Capabilities
- **Real-time Analysis**: Live data integration with vnstock library
- **Deep Insights**: Market maker behavior, smart money flow, institutional patterns
- **Risk Management**: Comprehensive risk assessment with precise stop-loss and target levels
- **Web Interface**: User-friendly Streamlit dashboard for interactive analysis
- **Deployment Ready**: Docker containerization for easy deployment

## 📈 Analysis Components

### 1. Smart Money Tracking
- Volume analysis and institutional flow detection
- Stealth accumulation and distribution patterns
- Price efficiency and market microstructure analysis
- Time-based trading pattern recognition

### 2. EIC Framework
- **Environment**: Market conditions, sector trends, regulatory environment
- **Infrastructure**: Business model strength, operational efficiency, management quality
- **Competitiveness**: Market position, competitive advantages, growth trajectory

### 3. Market Maker Analysis
- Trading style classification (Professional/Active/Opportunistic)
- Market phase identification (Accumulation/Markup/Distribution/Consolidation)
- Liquidity provision quality assessment
- Price discovery efficiency measurement

### 4. Technical Analysis
- 52-week pattern analysis with momentum indicators
- Support/resistance level identification
- Multi-timeframe trend analysis
- Volume-price relationship assessment

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)

### Local Installation
```bash
# Clone the repository
git clone <repository-url>
cd vietnam-stock-analysis

# Install dependencies
pip install -r requirements.txt

# Run the web application
streamlit run web_app.py
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Access the application
open http://localhost:8501
```

### Cloud Deployment Options

#### 1. Heroku Deployment
```bash
# Create Heroku app
heroku create vietnam-stock-analyzer

# Configure buildpacks
heroku buildpacks:set heroku/python

# Deploy
git push heroku main
```

#### 2. AWS EC2 Deployment
```bash
# Launch EC2 instance with Docker
# Clone repository and run:
docker-compose up -d

# Configure security groups for port 8501
```

#### 3. Google Cloud Run
```bash
# Build container
docker build -t gcr.io/PROJECT-ID/vietnam-stock-analyzer .

# Deploy to Cloud Run
gcloud run deploy vietnam-stock-analyzer \
  --image gcr.io/PROJECT-ID/vietnam-stock-analyzer \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## 📊 Usage Examples

### 1. Comprehensive Analysis
```python
from comprehensive_stock_reporter import ComprehensiveStockReporter

reporter = ComprehensiveStockReporter()
report = reporter.generate_comprehensive_report('VCB', 'Banks')

print(f"Composite Score: {report['composite_score']['composite_score']}")
print(f"Recommendation: {report['executive_summary']['recommended_action']}")
```

### 2. Smart Money Signals
```python
from smart_money_signal_system import SmartMoneySignalSystem

signal_system = SmartMoneySignalSystem()
signals = signal_system.generate_smart_money_signals('FPT')

print(f"Signal Classification: {signals['composite_signal_score']['signal_classification']}")
print(f"Entry Signals: {signals['entry_exit_signals']['entry_signals']}")
```

### 3. EIC Analysis
```python
from eic_framework import EICFramework

eic = EICFramework()
analysis = eic.calculate_comprehensive_eic_score('VIC', 'Real_Estate')

print(f"EIC Score: {analysis['eic_score']}")
print(f"Investment Grade: {analysis['investment_grade']}")
```

## 🎯 Web Interface Features

### Dashboard Sections
1. **📊 Comprehensive Analysis**: Full multi-factor analysis with executive summary
2. **🎯 Smart Money Signals**: Trading signals with entry/exit levels
3. **🏢 EIC Framework**: Top-down investment analysis
4. **💹 Market Maker Analysis**: Market structure and maker behavior
5. **🌏 Stock Universe**: Sector breakdown and stock discovery
6. **📈 Multi-Stock Comparison**: Relative analysis of multiple stocks

### Interactive Elements
- Real-time stock selection and analysis
- Interactive charts and visualizations
- Risk assessment with color-coded alerts
- Downloadable reports and analysis data

## ⚠️ Risk Management Features

### Comprehensive Risk Assessment
- **Volatility Metrics**: Daily, annualized, and downside volatility
- **Liquidity Risk**: Volume consistency and market depth analysis
- **Market Risk**: Correlation and systematic risk factors
- **Position Risk**: Optimal position sizing and risk-reward ratios

### Stop Loss and Target Levels
- Multiple stop-loss levels (Conservative/Moderate/Aggressive)
- Fibonacci-based target levels
- Risk-reward ratio calculations
- Position sizing recommendations

## 📈 Performance Metrics

### Analysis Accuracy
- **Signal Success Rate**: Historical performance of entry/exit signals
- **Risk-Adjusted Returns**: Sharpe ratio optimization
- **Market Outperformance**: Benchmark comparison tracking

### System Performance
- **Analysis Speed**: Sub-30 second comprehensive reports
- **Data Coverage**: 500+ liquid Vietnamese stocks
- **Update Frequency**: Daily market data integration
- **Uptime**: 99.5%+ availability target

## 🔧 Configuration

### Environment Variables
```bash
# API Configuration
VNSTOCK_API_KEY=your_api_key_here
CACHE_TTL_MINUTES=30

# Database Configuration (optional)
DATABASE_URL=postgresql://user:pass@localhost/vietnam_stocks
REDIS_URL=redis://localhost:6379

# Logging
LOG_LEVEL=INFO
LOG_FILE=vietnam_stock_analyzer.log
```

### Custom Settings
- Modify `signal_config` in `SmartMoneySignalSystem` for signal sensitivity
- Adjust `eic_weights` in `EICFramework` for scoring preferences
- Update `liquidity_filters` in `VietnamStockUniverse` for stock universe criteria

## 📚 API Reference

### Core Classes
- `ComprehensiveStockReporter`: Main analysis orchestrator
- `SmartMoneySignalSystem`: Signal generation and detection
- `EICFramework`: Environment-Infrastructure-Competitiveness analysis
- `MarketMakerAnalyzer`: Market maker behavior analysis
- `VietnamStockUniverse`: Stock discovery and classification

### Key Methods
```python
# Generate comprehensive analysis
report = reporter.generate_comprehensive_report(symbol, sector)

# Get smart money signals
signals = signal_system.generate_smart_money_signals(symbol)

# Calculate EIC score
eic_score = eic_framework.calculate_comprehensive_eic_score(symbol, sector)

# Analyze market maker behavior
mm_analysis = mm_analyzer.analyze_market_maker_style(symbol)
```

## 🚀 Future Enhancements

### Planned Features
- **Real-time Alerts**: WebSocket integration for live signal updates
- **Portfolio Analysis**: Multi-stock portfolio optimization
- **Sector Rotation**: Automated sector strength analysis
- **Machine Learning**: Enhanced prediction models
- **Mobile App**: React Native mobile interface

### Data Enhancements
- **Fundamental Data**: Earnings, financials, and ratios integration
- **News Sentiment**: Natural language processing for news impact
- **Social Media**: Retail sentiment tracking
- **Economic Indicators**: Macro data integration

## 📞 Support & Documentation

### Getting Help
- **Documentation**: Comprehensive inline documentation in all modules
- **Examples**: Sample analysis scripts in `examples/` directory
- **Issues**: GitHub issues for bug reports and feature requests
- **Discussions**: Community discussion forum

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with comprehensive tests
4. Submit a pull request with detailed description

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This system is for educational and research purposes only. Not financial advice. Always consult with qualified financial advisors before making investment decisions. Past performance does not guarantee future results.

---

**Built with ❤️ for the Vietnamese stock market analysis community**