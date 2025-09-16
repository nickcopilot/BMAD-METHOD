#!/usr/bin/env python3
"""
Beta Performance Monitoring and Analytics System
Tracks beta tester behavior, signal accuracy, and system performance
"""

import sqlite3
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class BetaMonitoringSystem:
    """Comprehensive monitoring system for beta testing program"""

    def __init__(self, db_path: str = "data/beta_vietnam_stocks.db"):
        self.db_path = db_path
        self.setup_logging()
        self.init_monitoring_tables()

        # Email configuration for alerts
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

    def setup_logging(self):
        """Setup logging for monitoring system"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/beta_monitoring.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def init_monitoring_tables(self):
        """Initialize database tables for monitoring"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # User activity tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                session_id TEXT,
                action_type TEXT NOT NULL,
                action_details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                page_url TEXT,
                user_agent TEXT,
                duration_seconds INTEGER,
                FOREIGN KEY (user_id) REFERENCES beta_users (id)
            )
        ''')

        # Signal performance tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                signal_id TEXT NOT NULL,
                stock_symbol TEXT NOT NULL,
                predicted_direction TEXT NOT NULL,
                confidence_score REAL,
                signal_date DATETIME NOT NULL,
                entry_price REAL,
                exit_price REAL,
                actual_return REAL,
                predicted_return REAL,
                accuracy INTEGER, -- 1 for correct, 0 for incorrect
                tracking_method TEXT, -- 'paper' or 'real'
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES beta_users (id)
            )
        ''')

        # System performance metrics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_unit TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                additional_data TEXT
            )
        ''')

        # Error tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS error_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                error_type TEXT NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                page_url TEXT,
                user_agent TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')

        # Feature usage tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feature_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                feature_name TEXT NOT NULL,
                usage_count INTEGER DEFAULT 1,
                first_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP,
                total_time_spent INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES beta_users (id),
                UNIQUE(user_id, feature_name)
            )
        ''')

        conn.commit()
        conn.close()
        self.logger.info("Beta monitoring tables initialized")

    def track_user_activity(self, user_id: int, action_type: str,
                           action_details: str = None, session_id: str = None,
                           page_url: str = None, user_agent: str = None,
                           duration_seconds: int = None):
        """Track user activity for analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO user_activity
            (user_id, session_id, action_type, action_details, page_url, user_agent, duration_seconds)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, session_id, action_type, action_details, page_url, user_agent, duration_seconds))

        conn.commit()
        conn.close()

        self.logger.info(f"Tracked activity: User {user_id} - {action_type}")

    def track_signal_performance(self, user_id: int, signal_data: Dict,
                               actual_result: Dict = None):
        """Track signal performance for validation"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        signal_id = signal_data.get('signal_id', f"signal_{datetime.now().strftime('%Y%m%d_%H%M%S')}")

        # Calculate accuracy if actual result provided
        accuracy = None
        if actual_result:
            predicted_direction = signal_data.get('direction', 'unknown')
            actual_direction = actual_result.get('direction', 'unknown')
            accuracy = 1 if predicted_direction == actual_direction else 0

        cursor.execute('''
            INSERT INTO signal_performance
            (user_id, signal_id, stock_symbol, predicted_direction, confidence_score,
             signal_date, entry_price, exit_price, actual_return, predicted_return,
             accuracy, tracking_method, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, signal_id, signal_data.get('symbol'),
            signal_data.get('direction'), signal_data.get('confidence'),
            signal_data.get('date'), actual_result.get('entry_price') if actual_result else None,
            actual_result.get('exit_price') if actual_result else None,
            actual_result.get('return') if actual_result else None,
            signal_data.get('expected_return'),
            accuracy, actual_result.get('method', 'paper') if actual_result else 'paper',
            actual_result.get('notes') if actual_result else None
        ))

        conn.commit()
        conn.close()

        self.logger.info(f"Tracked signal performance: User {user_id} - {signal_data.get('symbol')}")

    def record_system_metric(self, metric_name: str, metric_value: float,
                           metric_unit: str = None, additional_data: Dict = None):
        """Record system performance metrics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        additional_json = json.dumps(additional_data) if additional_data else None

        cursor.execute('''
            INSERT INTO system_metrics (metric_name, metric_value, metric_unit, additional_data)
            VALUES (?, ?, ?, ?)
        ''', (metric_name, metric_value, metric_unit, additional_json))

        conn.commit()
        conn.close()

    def log_error(self, error_type: str, error_message: str,
                  user_id: int = None, stack_trace: str = None,
                  page_url: str = None, user_agent: str = None):
        """Log errors for tracking and resolution"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO error_logs
            (user_id, error_type, error_message, stack_trace, page_url, user_agent)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, error_type, error_message, stack_trace, page_url, user_agent))

        conn.commit()
        conn.close()

        self.logger.error(f"Error logged: {error_type} - {error_message}")

        # Send email alert for critical errors
        if error_type in ['CRITICAL', 'SYSTEM_FAILURE']:
            self.send_error_alert(error_type, error_message, user_id)

    def track_feature_usage(self, user_id: int, feature_name: str, time_spent: int = 0):
        """Track feature usage statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Update existing record or create new one
        cursor.execute('''
            INSERT OR REPLACE INTO feature_usage
            (user_id, feature_name, usage_count, first_used, last_used, total_time_spent)
            VALUES (
                ?, ?,
                COALESCE((SELECT usage_count FROM feature_usage WHERE user_id = ? AND feature_name = ?), 0) + 1,
                COALESCE((SELECT first_used FROM feature_usage WHERE user_id = ? AND feature_name = ?), CURRENT_TIMESTAMP),
                CURRENT_TIMESTAMP,
                COALESCE((SELECT total_time_spent FROM feature_usage WHERE user_id = ? AND feature_name = ?), 0) + ?
            )
        ''', (user_id, feature_name, user_id, feature_name, user_id, feature_name, user_id, feature_name, time_spent))

        conn.commit()
        conn.close()

    def get_user_analytics(self, user_id: int = None, days: int = 7) -> Dict:
        """Get comprehensive user analytics"""
        conn = sqlite3.connect(self.db_path)

        since_date = datetime.now() - timedelta(days=days)

        # Base query conditions
        if user_id:
            user_filter = f"WHERE user_id = {user_id}"
            date_filter = f"WHERE timestamp >= '{since_date}'"
            user_date_filter = f"WHERE user_id = {user_id} AND timestamp >= '{since_date}'"
        else:
            user_filter = ""
            date_filter = f"WHERE timestamp >= '{since_date}'"
            user_date_filter = f"WHERE timestamp >= '{since_date}'"

        analytics = {}

        # User activity summary
        activity_df = pd.read_sql_query(f'''
            SELECT action_type, COUNT(*) as count, AVG(duration_seconds) as avg_duration
            FROM user_activity
            {user_date_filter}
            GROUP BY action_type
        ''', conn)
        analytics['activity_summary'] = activity_df.to_dict('records')

        # Signal performance summary
        signal_df = pd.read_sql_query(f'''
            SELECT
                COUNT(*) as total_signals,
                AVG(CASE WHEN accuracy = 1 THEN 1.0 ELSE 0.0 END) as accuracy_rate,
                AVG(actual_return) as avg_return,
                COUNT(DISTINCT stock_symbol) as unique_stocks
            FROM signal_performance
            {user_date_filter}
        ''', conn)
        analytics['signal_performance'] = signal_df.to_dict('records')[0] if not signal_df.empty else {}

        # Feature usage summary
        feature_df = pd.read_sql_query(f'''
            SELECT feature_name, SUM(usage_count) as total_usage, AVG(total_time_spent) as avg_time
            FROM feature_usage
            {user_filter}
            GROUP BY feature_name
            ORDER BY total_usage DESC
        ''', conn)
        analytics['feature_usage'] = feature_df.to_dict('records')

        # Daily engagement
        daily_df = pd.read_sql_query(f'''
            SELECT
                DATE(timestamp) as date,
                COUNT(DISTINCT user_id) as active_users,
                COUNT(*) as total_actions
            FROM user_activity
            {date_filter}
            GROUP BY DATE(timestamp)
            ORDER BY date
        ''', conn)
        analytics['daily_engagement'] = daily_df.to_dict('records')

        conn.close()
        return analytics

    def get_system_health(self) -> Dict:
        """Get current system health metrics"""
        conn = sqlite3.connect(self.db_path)

        health = {}

        # Recent errors
        error_df = pd.read_sql_query('''
            SELECT error_type, COUNT(*) as count
            FROM error_logs
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY error_type
        ''', conn)
        health['recent_errors'] = error_df.to_dict('records')

        # System metrics (last 24 hours)
        metrics_df = pd.read_sql_query('''
            SELECT metric_name, AVG(metric_value) as avg_value, MAX(metric_value) as max_value
            FROM system_metrics
            WHERE timestamp >= datetime('now', '-24 hours')
            GROUP BY metric_name
        ''', conn)
        health['system_metrics'] = metrics_df.to_dict('records')

        # Active users today
        active_users = pd.read_sql_query('''
            SELECT COUNT(DISTINCT user_id) as active_users
            FROM user_activity
            WHERE DATE(timestamp) = DATE('now')
        ''', conn).iloc[0]['active_users']
        health['active_users_today'] = active_users

        # Signal accuracy today
        today_accuracy = pd.read_sql_query('''
            SELECT AVG(CASE WHEN accuracy = 1 THEN 1.0 ELSE 0.0 END) as accuracy
            FROM signal_performance
            WHERE DATE(signal_date) = DATE('now') AND accuracy IS NOT NULL
        ''', conn)
        health['signal_accuracy_today'] = today_accuracy.iloc[0]['accuracy'] if not today_accuracy.empty else None

        conn.close()
        return health

    def generate_beta_report(self, days: int = 7) -> Dict:
        """Generate comprehensive beta testing report"""
        analytics = self.get_user_analytics(days=days)
        health = self.get_system_health()

        conn = sqlite3.connect(self.db_path)

        # Beta tester summary
        testers_df = pd.read_sql_query('''
            SELECT
                COUNT(*) as total_testers,
                COUNT(CASE WHEN last_login >= datetime('now', '-7 days') THEN 1 END) as active_testers,
                AVG(feedback_score) as avg_satisfaction
            FROM beta_users
        ''', conn)

        # Feedback summary
        feedback_df = pd.read_sql_query(f'''
            SELECT
                feedback_type,
                COUNT(*) as count,
                AVG(rating) as avg_rating
            FROM beta_feedback
            WHERE created_at >= datetime('now', '-{days} days')
            GROUP BY feedback_type
        ''', conn)

        conn.close()

        report = {
            'report_period': f"Last {days} days",
            'generated_at': datetime.now().isoformat(),
            'tester_summary': testers_df.to_dict('records')[0] if not testers_df.empty else {},
            'feedback_summary': feedback_df.to_dict('records'),
            'user_analytics': analytics,
            'system_health': health
        }

        return report

    def send_error_alert(self, error_type: str, error_message: str, user_id: int = None):
        """Send email alert for critical errors"""
        if not self.smtp_username or not self.smtp_password:
            self.logger.warning("Email credentials not configured, skipping alert")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.smtp_username  # Send to self for now
            msg['Subject'] = f"🚨 Beta System Alert: {error_type}"

            body = f"""
            Critical error detected in beta system:

            Error Type: {error_type}
            Error Message: {error_message}
            User ID: {user_id if user_id else 'System'}
            Timestamp: {datetime.now()}

            Please investigate immediately.
            """

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"Error alert sent for: {error_type}")

        except Exception as e:
            self.logger.error(f"Failed to send error alert: {e}")

    def export_analytics_report(self, filepath: str = None, days: int = 7):
        """Export comprehensive analytics report to JSON"""
        if not filepath:
            filepath = f"reports/beta_analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        report = self.generate_beta_report(days)

        # Ensure reports directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)

        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"Analytics report exported to: {filepath}")
        return filepath

# Usage example and monitoring utilities
def start_monitoring():
    """Start the monitoring system"""
    monitoring = BetaMonitoringSystem()

    # Record system startup
    monitoring.record_system_metric("system_startup", 1.0, "count")

    return monitoring

def monitor_streamlit_session(monitoring: BetaMonitoringSystem, user_id: int, session_id: str):
    """Monitor Streamlit session activity"""
    import streamlit as st

    # Track page load
    monitoring.track_user_activity(
        user_id=user_id,
        action_type="page_load",
        action_details=st.session_state.get('current_page', 'unknown'),
        session_id=session_id,
        page_url=st.session_state.get('current_url', 'unknown')
    )

    # Track feature usage when buttons are clicked
    def track_button_click(feature_name: str):
        monitoring.track_feature_usage(user_id, feature_name)
        monitoring.track_user_activity(
            user_id=user_id,
            action_type="button_click",
            action_details=feature_name,
            session_id=session_id
        )

    return track_button_click

if __name__ == "__main__":
    # Initialize monitoring system
    monitoring = start_monitoring()

    # Generate sample report
    report = monitoring.generate_beta_report(days=7)
    print("Beta Testing Report Generated:")
    print(json.dumps(report, indent=2, default=str))

    # Export report
    filepath = monitoring.export_analytics_report()
    print(f"\nReport exported to: {filepath}")