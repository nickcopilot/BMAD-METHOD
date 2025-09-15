# Bubble.io Dashboard Specification
## Vietnam Stock Analysis System

### Overview
No-code dashboard for screening stocks, monitoring portfolio, and generating alerts using data from your automated collection system.

## Dashboard Structure

### Page 1: Main Dashboard
**Layout**: Header + 4 main sections

#### Header Section
- **Title**: "Vietnam Stock Analysis System"
- **Date/Time**: Current date and last data update
- **Portfolio Summary**:
  - Total Value: [Dynamic from Portfolio sheet]
  - Day P&L: [Calculated field]
  - Day P&L %: [Color coded: Green >0, Red <0]

#### Section 1: Quick Stats (Top Row)
**4 Metric Cards**:
1. **Market Overview**
   - Total Stocks Tracked: 17
   - Average EIC Score: [Dynamic calculation]
   - Market Sentiment: [Based on avg change%]

2. **Best Performer**
   - Symbol: [From daily data]
   - Change %: [Color coded]
   - EIC Score: [Display]

3. **Portfolio Alerts**
   - Active Alerts: [Count from alerts]
   - Urgent: [High priority count]
   - Status: [Green/Yellow/Red indicator]

4. **Sector Leader**
   - Best Sector: [Highest avg change%]
   - Performance: [Percentage]
   - Trend: [Up/Down arrow]

#### Section 2: Sector Tabs (Main Content)
**4 Tabs**: Securities | Banks | Real Estate | Steel

**Each Tab Contains**:
- **Sector Performance Header**:
  - Sector Name + Average Change%
  - Average EIC Score
  - Number of stocks
  - Color indicator (Green/Yellow/Red)

- **Stock Table**:
  | Symbol | Company | Price | Change% | Volume | EIC Score | Signal | Action |
  |--------|---------|-------|---------|--------|-----------|--------|---------|
  | VCB    | Vietcombank | 66,000 | +0.00% | 1.5M | 5.9 | HOLD | [Details] |
  | BID    | BIDV    | 42,000 | +3.05% | 2.1M | 6.6 | BUY  | [Details] |

  **Color Coding**:
  - Change%: Green >0, Red <0
  - EIC Score: Green ≥7, Yellow 5-7, Red <5
  - Signal: Green (BUY), Yellow (HOLD), Red (SELL)

#### Section 3: Portfolio Monitor (Right Sidebar)
**Your Holdings Table**:
| Symbol | Qty | Avg Price | Current | P&L% | Alert |
|--------|-----|-----------|---------|------|-------|
| VCB    | 100 | 62,700    | 66,000  | +5.3% | ✅ |
| SSI    | 200 | 39,900    | 42,000  | +5.3% | ✅ |

**Portfolio Summary**:
- Total Investment: [Sum of cost basis]
- Current Value: [Sum of market value]
- Total P&L: [Absolute and percentage]
- Best/Worst Position: [Dynamic]

#### Section 4: Recent Alerts (Bottom)
**Alert Feed**:
- Timestamp | Type | Symbol | Message | Severity
- Auto-refresh every 5 minutes
- Click to dismiss or take action

### Page 2: Stock Detail View
**Triggered by**: Clicking any stock symbol

#### Stock Header
- **Company Name & Symbol**
- **Current Price & Change**
- **EIC Score Breakdown**:
  - Economy Score: [Visual bar chart]
  - Industry Score: [Visual bar chart]
  - Company Score: [Visual bar chart]
  - Total Score: [Large number with color]

#### EIC Analysis Sections
**Economy Analysis (30%)**:
- GDP Growth Impact: [Text explanation]
- Interest Rate Environment: [Text explanation]
- Currency Stability: [Text explanation]
- Overall Economy Score: [Number with explanation]

**Industry Analysis (40%)**:
- Sector Performance: [vs other sectors]
- Industry Trends: [Bullish/Bearish indicators]
- Competitive Position: [Relative to peers]
- Price Momentum: [Technical indicators]

**Company Analysis (30%)**:
- Financial Health: [Key ratios]
- Revenue Trends: [Growth indicators]
- Valuation: [P/E, P/B vs averages]
- Management Quality: [Qualitative assessment]

#### Investment Recommendation
**Large Card with**:
- **Signal**: BUY/HOLD/SELL (Large, colored text)
- **Target Price**: [Calculated estimate]
- **Risk Level**: Low/Medium/High
- **Time Horizon**: Short/Medium/Long term
- **Key Reasons**: Bullet points
- **Risks to Watch**: Bullet points

#### Action Buttons
- **Add to Portfolio**: [If not held]
- **Set Price Alert**: [Custom price trigger]
- **Generate Full Report**: [PDF export]
- **Add to Watchlist**: [For monitoring]

### Page 3: Portfolio Management
#### Holdings Overview
**Complete Portfolio Table**:
- All positions with full details
- Sortable by: Symbol, P&L%, EIC Score, Market Value
- Bulk actions: Set alerts, export data

#### Position Management
**For each holding**:
- **Edit Position**: Update quantity, avg price
- **Set Alerts**:
  - Price drop threshold (default -5%)
  - EIC score change (default ±1.0)
  - Volume spike (default 200%)
- **Performance Charts**: Historical P&L
- **Actions**: Sell signals, rebalancing suggestions

#### Portfolio Analytics
- **Sector Allocation**: Pie chart
- **Performance vs VN-Index**: Line chart
- **Risk Metrics**: Volatility, correlation
- **Dividend Tracking**: Expected income

### Page 4: Watchlist & Screening
#### Stock Screener
**Filter Controls**:
- **Sector**: Dropdown (All, Securities, Banks, Real Estate, Steel)
- **EIC Score Range**: Slider (1-10)
- **Price Change**: Dropdown (All, >+3%, +1% to +3%, etc.)
- **Volume**: Dropdown (Normal, High volume, Very high)
- **Signal**: Dropdown (All, Strong Buy, Buy, Hold, Sell)

**Results Table**:
- Filtered stocks meeting criteria
- Sortable by any column
- Quick actions: Add to portfolio, add to watchlist

#### Custom Watchlist
**Your Monitoring List**:
- Stocks you're considering but not yet holding
- Custom notes and target prices
- Alert when entering buy zone
- Easy promotion to portfolio

### Page 5: Reports & Analysis
#### On-Demand Report Generator
**Input Section**:
- **Stock Symbol**: Text input
- **Report Type**: Dropdown (Quick Analysis, Full Research, Comparison)
- **Generate Button**: Triggers report creation

**Report Display**:
- **Executive Summary**: Key findings
- **EIC Breakdown**: Detailed scores and reasoning
- **Investment Thesis**: Buy/Hold/Sell case
- **Risk Assessment**: Key risks and mitigations
- **Price Targets**: Conservative and optimistic
- **Export Options**: PDF, Email, Print

#### Historical Analysis
- **Performance Tracking**: How EIC scores predicted returns
- **Sector Rotation**: Which sectors are trending
- **Best Picks**: Highest performing recommendations
- **Learning Loop**: System accuracy improvements

## Data Integration

### Google Sheets Connection
**Data Sources**:
1. **Daily_Stock_Data**: Real-time stock prices and EIC scores
2. **Portfolio_Holdings**: Your actual positions
3. **Stock_Watchlist**: Monitoring list
4. **Alerts_Log**: System-generated alerts
5. **Sector_Analysis**: Sector performance data

**Update Frequency**:
- **Real-time**: Portfolio values (during market hours)
- **Daily**: Stock prices and EIC scores (evening update)
- **On-demand**: Report generation
- **Alerts**: Immediate when triggered

### Bubble.io Implementation Steps

#### Phase 1: Basic Structure (Week 1)
1. **Create Bubble app**: "Vietnam Stock Screener"
2. **Connect Google Sheets**: Import as data source
3. **Build main dashboard**: Header + sector tabs
4. **Test data display**: Verify stock data shows correctly

#### Phase 2: Interactive Features (Week 2)
1. **Add filtering**: Sector and EIC score filters
2. **Build stock detail**: Popup with EIC breakdown
3. **Portfolio tracker**: Holdings table with P&L
4. **Basic alerts**: Email notifications

#### Phase 3: Advanced Features (Week 3)
1. **Report generator**: On-demand analysis
2. **Charts and visuals**: EIC score charts
3. **Alert management**: Custom alert settings
4. **Export functions**: PDF reports

#### Phase 4: Polish & Automation (Week 4)
1. **UI improvements**: Better design and UX
2. **Mobile responsive**: Works on phone
3. **Performance optimization**: Faster loading
4. **User guide**: Help documentation

## Success Metrics
- **Daily Usage**: Check dashboard every evening
- **Decision Support**: Use EIC scores for stock picks
- **Alert Effectiveness**: Timely notifications help avoid losses
- **Portfolio Performance**: Better returns vs manual approach

## Budget Estimate
- **Bubble.io**: Free initially, $25/month (Personal plan) later
- **Google Sheets**: Free (sufficient for your data volume)
- **Total**: $25/month maximum

This dashboard will give you professional-grade stock analysis capabilities optimized for your Vietnam market focus and evening trading schedule.