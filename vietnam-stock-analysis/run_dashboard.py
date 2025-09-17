#!/usr/bin/env python3
"""
Vietnam Stock Analysis Dashboard Launcher
Runs the Streamlit dashboard with proper setup
"""

import subprocess
import sys
import os
import time

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")

    try:
        import streamlit
        import plotly
        import vnstock
        import pandas
        import numpy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_database():
    """Check if database exists and has data"""
    print("🗄️ Checking database...")

    db_path = "data/vietnam_stocks.db"
    if not os.path.exists(db_path):
        print("❌ Database not found. Run data collection first.")
        return False

    # Check if database has data
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT COUNT(*) FROM stocks")
        stock_count = cursor.fetchone()[0]
        cursor = conn.execute("SELECT COUNT(*) FROM price_data")
        price_count = cursor.fetchone()[0]
        conn.close()

        print(f"✅ Database found: {stock_count} stocks, {price_count} price records")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def run_data_collection():
    """Run data collection if needed"""
    print("📊 Running data collection...")

    try:
        result = subprocess.run([sys.executable, "test_collection.py"],
                              capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            print("✅ Data collection completed successfully")
            return True
        else:
            print(f"❌ Data collection failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⏰ Data collection timed out")
        return False
    except Exception as e:
        print(f"❌ Error running data collection: {e}")
        return False

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🚀 Launching dashboard...")

    # Change to correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Launch Streamlit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            "dashboard/main.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ]

        print("📱 Dashboard URL: http://localhost:8501")
        print("🔗 In Codespaces: Use the 'Ports' tab and open port 8501")
        print("⏹️ Press Ctrl+C to stop the dashboard")
        print("-" * 50)

        subprocess.run(cmd)

    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    """Main launcher function"""
    print("=" * 60)
    print("🇻🇳 Vietnam Stock Analysis Dashboard Launcher")
    print("=" * 60)

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Check database
    if not check_database():
        print("\n🔧 Attempting to collect initial data...")
        if not run_data_collection():
            print("❌ Failed to collect data. Please run manually:")
            print("   python test_collection.py")
            sys.exit(1)

    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()