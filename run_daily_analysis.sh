#!/bin/bash
# Vietnam Stock Analysis - Daily Startup Script

echo "🇻🇳 Vietnam Stock Analysis System - Daily Update"
echo "================================================"

# Check if Python environment is ready
if command -v python3 &> /dev/null; then
    echo "✅ Python environment ready"
else
    echo "❌ Python not found"
    exit 1
fi

# Run daily data collection
echo "📊 Collecting latest stock data..."
python3 code_analysis/daily_data_collector.py

# Check for alerts
echo "🚨 Checking portfolio alerts..."
python3 code_analysis/alert_system.py

# Generate summary
echo "📋 Daily analysis complete!"
echo ""
echo "Next steps:"
echo "1. Check session_logs/ for latest data files"
echo "2. Review daily_report_*.md for market summary"
echo "3. Update Google Sheets with new CSV data"
echo "4. Check Bubble.io dashboard for latest analysis"
echo ""
echo "Happy investing! 🚀"
