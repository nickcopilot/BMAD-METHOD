# How to Download CSV Files for Google Sheets

## Your Vietnam Stock Analysis CSV Files Are Ready!

### Files to Download (in order):
1. **01_Daily_Stock_Data.csv** - Current stock prices and EIC scores
2. **02_Portfolio_Holdings.csv** - Your sample portfolio
3. **03_Stock_Watchlist.csv** - Stocks you're monitoring
4. **04_Economic_Indicators.csv** - Vietnam macro data
5. **05_Sector_Analysis.csv** - Sector performance comparison
6. **06_Alerts_Log.csv** - System alerts and notifications

## Download Methods:

### Method 1: Individual File Download
1. In VS Code file explorer, navigate to `google_sheets_import/` folder
2. Right-click each CSV file → "Download"
3. Save to your computer

### Method 2: Git Clone (if you have git)
```bash
git clone https://github.com/nickcopilot/BMAD-METHOD.git
cd BMAD-METHOD/google_sheets_import/
```

### Method 3: Via Command Line (in VS Code Terminal)
```bash
# Show file contents to copy-paste
cat google_sheets_import/01_Daily_Stock_Data.csv
```

## After Download - Google Sheets Setup:

### Step 1: Create New Google Sheet
1. Go to sheets.google.com
2. Create new blank spreadsheet
3. Name it: "Vietnam Stock Analysis System"

### Step 2: Import Each CSV File as Separate Sheet
1. Click + at bottom to add new sheet
2. Name it same as CSV file (without numbers)
3. File → Import → Upload → Choose CSV file
4. Select "Replace current sheet"
5. Repeat for all 6 files

### Step 3: Your Dashboard is Ready!
- 6 sheets with live Vietnam stock data
- Ready to connect to Bubble.io dashboard
- Portfolio tracking operational
- EIC scores calculated and displayed

## Need Help?
- Each CSV file is small (under 1KB)
- Contains sample data from your Vietnam stocks
- Ready for immediate use in investment analysis

🚀 **Next**: Set up Bubble.io dashboard using these Google Sheets!