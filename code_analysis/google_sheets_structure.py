#!/usr/bin/env python3
"""
Google Sheets Structure for Vietnam Stock Analysis System
Creates CSV templates that can be uploaded to Google Sheets
"""

import pandas as pd
import csv
from datetime import datetime
import json

def create_daily_stock_data_sheet():
    """Create Daily Stock Data sheet structure"""
    columns = [
        'Date',
        'Symbol',
        'Company_Name',
        'Sector',
        'Current_Price',
        'Previous_Close',
        'Change_Pct',
        'Volume',
        'High',
        'Low',
        'EIC_Score',
        'Economy_Score',
        'Industry_Score',
        'Company_Score',
        'Signal',
        'Last_Updated'
    ]

    # Create sample data
    sample_data = [
        ['2024-09-15', 'VCB', 'Vietcombank', 'Banks', 66000, 66000, 0.00, 1500000, 67000, 65500, 5.2, 5.0, 5.5, 5.0, 'HOLD', '2024-09-15 08:39:31'],
        ['2024-09-15', 'BID', 'BIDV', 'Banks', 42000, 40800, 3.05, 2100000, 42500, 40500, 5.8, 5.0, 7.0, 5.0, 'HOLD', '2024-09-15 08:39:31'],
        ['2024-09-15', 'SSI', 'SSI Securities', 'Securities', 42000, 41700, 0.72, 980000, 42300, 41500, 5.4, 5.0, 6.0, 5.0, 'HOLD', '2024-09-15 08:39:31'],
        ['2024-09-15', 'HPG', 'Hoa Phat Group', 'Steel', 30000, 29650, 1.17, 1800000, 30200, 29500, 5.4, 5.0, 6.0, 5.0, 'HOLD', '2024-09-15 08:39:31'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)
    return df, 'Daily_Stock_Data'

def create_portfolio_sheet():
    """Create Portfolio Holdings sheet structure"""
    columns = [
        'Symbol',
        'Company_Name',
        'Sector',
        'Quantity',
        'Avg_Price',
        'Current_Price',
        'Market_Value',
        'Total_Cost',
        'Unrealized_PnL',
        'Unrealized_PnL_Pct',
        'EIC_Score',
        'Signal',
        'Alert_Status',
        'Price_Alert_Level',
        'EIC_Alert_Threshold',
        'Last_Updated'
    ]

    # Sample portfolio data
    sample_data = [
        ['VCB', 'Vietcombank', 'Banks', 100, 62700, 66000, 6600000, 6270000, 330000, 5.26, 5.2, 'HOLD', 'OK', 59415, 1.0, '2024-09-15 08:39:31'],
        ['SSI', 'SSI Securities', 'Securities', 200, 39900, 42000, 8400000, 7980000, 420000, 5.26, 5.4, 'HOLD', 'OK', 37905, 1.0, '2024-09-15 08:39:31'],
        ['HPG', 'Hoa Phat Group', 'Steel', 150, 28500, 30000, 4500000, 4275000, 225000, 5.26, 5.4, 'HOLD', 'OK', 27075, 1.0, '2024-09-15 08:39:31'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)
    return df, 'Portfolio_Holdings'

def create_watchlist_sheet():
    """Create Stock Watchlist sheet structure"""
    columns = [
        'Symbol',
        'Company_Name',
        'Sector',
        'Current_Price',
        'Change_Pct',
        'EIC_Score',
        'Signal',
        'Target_Price',
        'Entry_Price_Alert',
        'Notes',
        'Date_Added',
        'Last_Updated'
    ]

    # Sample watchlist
    sample_data = [
        ['VCI', 'VCI Securities', 'Securities', 45000, 1.92, 5.4, 'HOLD', 50000, 43000, 'Monitor for breakout', '2024-09-15', '2024-09-15 08:39:31'],
        ['VHM', 'Vinhomes', 'Real_Estate', 104000, -0.95, 4.6, 'HOLD', 110000, 100000, 'RE sector recovery play', '2024-09-15', '2024-09-15 08:39:31'],
        ['CTG', 'VietinBank', 'Banks', 0, 0, 0, 'RESEARCH', 35000, 32000, 'Banking sector diversification', '2024-09-15', '2024-09-15 08:39:31'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)
    return df, 'Stock_Watchlist'

def create_economic_indicators_sheet():
    """Create Economic Indicators sheet structure"""
    columns = [
        'Date',
        'GDP_Growth_Rate',
        'Inflation_Rate_CPI',
        'Policy_Interest_Rate',
        'USD_VND_Rate',
        'Manufacturing_PMI',
        'Industrial_Production_Index',
        'Export_Growth_Rate',
        'Import_Growth_Rate',
        'Credit_Growth_Rate',
        'Foreign_Investment_Flow',
        'Stock_Market_Turnover',
        'VN_Index',
        'VN_Index_Change_Pct',
        'Economic_Sentiment_Score',
        'Source',
        'Last_Updated'
    ]

    # Sample economic data
    sample_data = [
        ['2024-Q3', 6.8, 2.6, 4.5, 24850, 52.7, 8.9, 15.2, 12.1, 9.5, 2.8, 18500, 1280, 1.2, 6.2, 'GSO.gov.vn', '2024-09-15'],
        ['2024-Q2', 6.9, 2.3, 4.5, 24780, 54.1, 9.2, 14.8, 11.8, 9.2, 3.1, 17800, 1265, -0.8, 6.5, 'GSO.gov.vn', '2024-08-15'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)
    return df, 'Economic_Indicators'

def create_sector_analysis_sheet():
    """Create Sector Analysis sheet structure"""
    columns = [
        'Date',
        'Sector',
        'Avg_Price_Change_Pct',
        'Avg_Volume_Change_Pct',
        'Avg_EIC_Score',
        'Top_Performer',
        'Top_Performer_Change',
        'Worst_Performer',
        'Worst_Performer_Change',
        'Sector_PE_Ratio',
        'Sector_PB_Ratio',
        'Market_Cap_Billion_VND',
        'Foreign_Ownership_Pct',
        'Sector_Momentum_Score',
        'Sector_Signal',
        'Key_News_Summary',
        'Last_Updated'
    ]

    # Sample sector analysis
    sample_data = [
        ['2024-09-15', 'Banks', 1.53, 15.2, 5.2, 'BID', 3.05, 'CTG', -1.2, 8.2, 1.1, 850, 47.5, 6.1, 'HOLD', 'Credit growth remains strong', '2024-09-15 08:39:31'],
        ['2024-09-15', 'Securities', 1.32, 22.8, 5.4, 'VCI', 1.92, 'HCM', -0.5, 12.5, 1.8, 180, 35.2, 5.9, 'HOLD', 'Trading volumes increasing', '2024-09-15 08:39:31'],
        ['2024-09-15', 'Real_Estate', -0.47, -8.3, 4.6, 'DXG', 2.1, 'VHM', -0.95, 15.8, 1.2, 620, 28.9, 4.2, 'HOLD', 'Mixed signals in sector', '2024-09-15 08:39:31'],
        ['2024-09-15', 'Steel', 1.07, 18.5, 5.4, 'HPG', 1.17, 'NKG', 0.2, 9.8, 0.9, 320, 42.1, 5.8, 'HOLD', 'Infrastructure demand rising', '2024-09-15 08:39:31'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)
    return df, 'Sector_Analysis'

def create_alerts_log_sheet():
    """Create Alerts Log sheet structure"""
    columns = [
        'Timestamp',
        'Alert_Type',
        'Symbol',
        'Alert_Message',
        'Trigger_Value',
        'Current_Value',
        'Severity',
        'Status',
        'Action_Taken',
        'Notes'
    ]

    # Sample alerts
    sample_data = [
        ['2024-09-15 08:39:31', 'Price_Drop', 'VHM', 'Price dropped >2% in 1 day', -2.0, -0.95, 'Medium', 'Active', 'Email_Sent', 'Monitor for further decline'],
        ['2024-09-15 07:15:22', 'Volume_Spike', 'BID', 'Volume >200% of average', 200, 240, 'High', 'Active', 'Email_Sent', 'Potential news catalyst'],
    ]

    df = pd.DataFrame(sample_data, columns=columns)
    return df, 'Alerts_Log'

def generate_all_sheets():
    """Generate all Google Sheets structures"""
    print("📊 Creating Google Sheets Structure for Vietnam Stock Analysis")
    print("=" * 60)

    sheets = [
        create_daily_stock_data_sheet(),
        create_portfolio_sheet(),
        create_watchlist_sheet(),
        create_economic_indicators_sheet(),
        create_sector_analysis_sheet(),
        create_alerts_log_sheet()
    ]

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    for df, sheet_name in sheets:
        # Save as CSV for easy Google Sheets import
        filename = f'/workspaces/BMAD-METHOD/session_logs/{sheet_name}_{timestamp}.csv'
        df.to_csv(filename, index=False, encoding='utf-8')

        print(f"✅ {sheet_name:20} | {len(df)} rows | {len(df.columns)} columns")
        print(f"   📁 Saved to: {filename}")

    # Create import instructions
    create_import_instructions(timestamp)

    print(f"\n🚀 All sheets created! Ready for Google Sheets import.")

def create_import_instructions(timestamp):
    """Create instructions for importing to Google Sheets"""
    instructions = f"""
# Google Sheets Import Instructions - {timestamp}

## Step 1: Create New Google Sheet
1. Go to sheets.google.com
2. Create new blank spreadsheet
3. Name it: "Vietnam Stock Analysis System"

## Step 2: Import Each CSV File
Upload each CSV file as a separate sheet in your workbook:

### Sheet 1: Daily_Stock_Data_{timestamp}.csv
- Contains: Daily price data and EIC scores for all tracked stocks
- Purpose: Historical record and trend analysis
- Update frequency: Daily (evening)

### Sheet 2: Portfolio_Holdings_{timestamp}.csv
- Contains: Your actual stock holdings with P&L tracking
- Purpose: Portfolio monitoring and alert triggers
- Update frequency: Real-time during market hours

### Sheet 3: Stock_Watchlist_{timestamp}.csv
- Contains: Stocks you're monitoring but not yet holding
- Purpose: Opportunity identification and entry alerts
- Update frequency: As needed

### Sheet 4: Economic_Indicators_{timestamp}.csv
- Contains: Macro economic data from GSO.gov.vn
- Purpose: Economy-level EIC analysis
- Update frequency: Monthly/Quarterly

### Sheet 5: Sector_Analysis_{timestamp}.csv
- Contains: Sector-level performance and metrics
- Purpose: Industry-level EIC analysis
- Update frequency: Daily

### Sheet 6: Alerts_Log_{timestamp}.csv
- Contains: All system-generated alerts and notifications
- Purpose: Alert history and action tracking
- Update frequency: Real-time

## Step 3: Set Up Automation (Next Steps)
1. Connect Zapier to your Google Sheets
2. Set up PythonAnywhere for daily data collection
3. Configure Bubble.io dashboard to read from Sheets

## Step 4: Share Sheet for API Access
1. Click "Share" button in top-right
2. Set to "Anyone with link can view"
3. Copy the sheet URL for Bubble.io integration

Your Vietnam stock analysis system foundation is ready!
"""

    with open(f'/workspaces/BMAD-METHOD/documentation/google_sheets_import_instructions_{timestamp}.md', 'w') as f:
        f.write(instructions)

    print(f"📋 Import instructions saved to: google_sheets_import_instructions_{timestamp}.md")

if __name__ == "__main__":
    generate_all_sheets()