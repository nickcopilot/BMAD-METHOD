#!/usr/bin/env python3
"""
Beta User Management and Onboarding System
Handles beta user registration, authentication, feedback collection, and analytics
"""

import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import json
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
import plotly.graph_objects as go
import plotly.express as px

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class BetaUser:
    user_id: str
    email: str
    name: str
    role: str  # trader, analyst, investor, professional
    experience: str  # beginner, intermediate, expert
    portfolio_size: str  # small, medium, large
    signup_date: datetime
    last_active: datetime
    feedback_count: int
    signals_tracked: int
    is_active: bool

class BetaUserManager:
    def __init__(self, db_path: str = "data/beta_users.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize beta user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Beta users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS beta_users (
                user_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL,
                experience TEXT NOT NULL,
                portfolio_size TEXT NOT NULL,
                signup_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT TRUE,
                beta_code TEXT UNIQUE,
                referral_code TEXT,
                onboarding_completed BOOLEAN DEFAULT FALSE
            )
        ''')

        # User sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_sessions (
                session_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logout_time TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES beta_users (user_id)
            )
        ''')

        # Feedback table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS beta_feedback (
                feedback_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                feedback_type TEXT NOT NULL,
                feedback_text TEXT NOT NULL,
                rating INTEGER,
                feature_category TEXT,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'new',
                response TEXT,
                FOREIGN KEY (user_id) REFERENCES beta_users (user_id)
            )
        ''')

        # Signal tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signal_tracking (
                tracking_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                symbol TEXT NOT NULL,
                signal_date DATE NOT NULL,
                predicted_action TEXT NOT NULL,
                predicted_score REAL NOT NULL,
                actual_outcome TEXT,
                actual_return REAL,
                accuracy_score REAL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES beta_users (user_id)
            )
        ''')

        # User analytics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_analytics (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                event_data TEXT,
                page_url TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES beta_users (user_id)
            )
        ''')

        conn.commit()
        conn.close()
        logger.info("Beta user database initialized")

    def generate_beta_code(self) -> str:
        """Generate unique beta access code"""
        return secrets.token_urlsafe(12)

    def hash_password(self, password: str) -> str:
        """Hash password for storage"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_beta_user(self, email: str, name: str, password: str,
                          role: str, experience: str, portfolio_size: str,
                          referral_code: Optional[str] = None) -> Dict:
        """Register new beta user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Check if email already exists
            cursor.execute('SELECT email FROM beta_users WHERE email = ?', (email,))
            if cursor.fetchone():
                return {'success': False, 'error': 'Email already registered'}

            # Generate user ID and beta code
            user_id = secrets.token_urlsafe(16)
            beta_code = self.generate_beta_code()
            hashed_password = self.hash_password(password)

            # Insert new user
            cursor.execute('''
                INSERT INTO beta_users
                (user_id, email, name, hashed_password, role, experience, portfolio_size, beta_code, referral_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, email, name, hashed_password, role, experience, portfolio_size, beta_code, referral_code))

            conn.commit()
            conn.close()

            # Send welcome email
            self.send_welcome_email(email, name, beta_code)

            return {
                'success': True,
                'user_id': user_id,
                'beta_code': beta_code,
                'message': 'Registration successful! Check your email for beta access instructions.'
            }

        except Exception as e:
            logger.error(f"Registration error: {e}")
            return {'success': False, 'error': str(e)}

    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate beta user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            hashed_password = self.hash_password(password)
            cursor.execute('''
                SELECT user_id, name, is_active FROM beta_users
                WHERE email = ? AND hashed_password = ?
            ''', (email, hashed_password))

            result = cursor.fetchone()
            if result:
                user_id, name, is_active = result
                if is_active:
                    # Update last active
                    cursor.execute('UPDATE beta_users SET last_active = ? WHERE user_id = ?',
                                 (datetime.now(), user_id))
                    conn.commit()
                    conn.close()

                    return {
                        'success': True,
                        'user_id': user_id,
                        'name': name,
                        'message': 'Login successful'
                    }
                else:
                    conn.close()
                    return {'success': False, 'error': 'Account deactivated'}
            else:
                conn.close()
                return {'success': False, 'error': 'Invalid credentials'}

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return {'success': False, 'error': str(e)}

    def get_user_profile(self, user_id: str) -> Optional[BetaUser]:
        """Get beta user profile"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT user_id, email, name, role, experience, portfolio_size,
                       signup_date, last_active, is_active
                FROM beta_users WHERE user_id = ?
            ''', (user_id,))

            result = cursor.fetchone()
            if result:
                # Get feedback count
                cursor.execute('SELECT COUNT(*) FROM beta_feedback WHERE user_id = ?', (user_id,))
                feedback_count = cursor.fetchone()[0]

                # Get signals tracked count
                cursor.execute('SELECT COUNT(*) FROM signal_tracking WHERE user_id = ?', (user_id,))
                signals_tracked = cursor.fetchone()[0]

                conn.close()

                return BetaUser(
                    user_id=result[0],
                    email=result[1],
                    name=result[2],
                    role=result[3],
                    experience=result[4],
                    portfolio_size=result[5],
                    signup_date=datetime.fromisoformat(result[6]),
                    last_active=datetime.fromisoformat(result[7]),
                    feedback_count=feedback_count,
                    signals_tracked=signals_tracked,
                    is_active=result[8]
                )

            conn.close()
            return None

        except Exception as e:
            logger.error(f"Get user profile error: {e}")
            return None

    def get_all_beta_users(self) -> List[Dict]:
        """Get all beta users with their details"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                SELECT user_id, email, name, role, experience, portfolio_size,
                       signup_date, last_active, is_active
                FROM beta_users
                ORDER BY signup_date DESC
            ''')

            results = cursor.fetchall()
            conn.close()

            users = []
            for row in results:
                users.append({
                    'id': row[0],
                    'email': row[1],
                    'full_name': row[2],
                    'role': row[3],
                    'experience': row[4],
                    'portfolio_size': row[5],
                    'created_at': row[6],
                    'last_login': row[7],
                    'approved': row[8],  # Using is_active as approved
                    'referral_source': 'direct'  # Default value for compatibility
                })

            return users

        except Exception as e:
            logger.error(f"Get all beta users error: {e}")
            return []

    def submit_feedback(self, user_id: str, feedback_type: str, feedback_text: str,
                       rating: Optional[int] = None, feature_category: Optional[str] = None) -> bool:
        """Submit beta feedback"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO beta_feedback
                (user_id, feedback_type, feedback_text, rating, feature_category)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, feedback_type, feedback_text, rating, feature_category))

            conn.commit()
            conn.close()

            logger.info(f"Feedback submitted by user {user_id}: {feedback_type}")
            return True

        except Exception as e:
            logger.error(f"Submit feedback error: {e}")
            return False

    def track_signal_performance(self, user_id: str, symbol: str, signal_date: str,
                               predicted_action: str, predicted_score: float,
                               actual_outcome: Optional[str] = None,
                               actual_return: Optional[float] = None,
                               notes: Optional[str] = None) -> bool:
        """Track signal performance"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            # Calculate accuracy if actual outcome provided
            accuracy_score = None
            if actual_outcome and predicted_action:
                if (predicted_action == 'BUY' and actual_return and actual_return > 0) or \
                   (predicted_action == 'SELL' and actual_return and actual_return < 0):
                    accuracy_score = 1.0
                else:
                    accuracy_score = 0.0

            cursor.execute('''
                INSERT OR REPLACE INTO signal_tracking
                (user_id, symbol, signal_date, predicted_action, predicted_score,
                 actual_outcome, actual_return, accuracy_score, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, symbol, signal_date, predicted_action, predicted_score,
                  actual_outcome, actual_return, accuracy_score, notes))

            conn.commit()
            conn.close()

            return True

        except Exception as e:
            logger.error(f"Track signal performance error: {e}")
            return False

    def log_user_event(self, user_id: str, event_type: str, event_data: Dict, page_url: str = None):
        """Log user analytics event"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO user_analytics (user_id, event_type, event_data, page_url)
                VALUES (?, ?, ?, ?)
            ''', (user_id, event_type, json.dumps(event_data), page_url))

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"Log user event error: {e}")

    def get_beta_analytics(self) -> Dict:
        """Get comprehensive beta analytics"""
        try:
            conn = sqlite3.connect(self.db_path)

            # User statistics
            total_users = pd.read_sql_query('SELECT COUNT(*) as count FROM beta_users', conn).iloc[0]['count']
            active_users = pd.read_sql_query('SELECT COUNT(*) as count FROM beta_users WHERE is_active = 1', conn).iloc[0]['count']

            # Feedback statistics
            feedback_stats = pd.read_sql_query('''
                SELECT feedback_type, COUNT(*) as count, AVG(rating) as avg_rating
                FROM beta_feedback
                GROUP BY feedback_type
            ''', conn)

            # Signal tracking statistics
            signal_stats = pd.read_sql_query('''
                SELECT
                    COUNT(*) as total_signals,
                    AVG(accuracy_score) as avg_accuracy,
                    AVG(actual_return) as avg_return
                FROM signal_tracking
                WHERE accuracy_score IS NOT NULL
            ''', conn)

            # User engagement
            engagement_stats = pd.read_sql_query('''
                SELECT
                    DATE(last_active) as date,
                    COUNT(*) as active_users
                FROM beta_users
                WHERE last_active >= date('now', '-7 days')
                GROUP BY DATE(last_active)
                ORDER BY date
            ''', conn)

            conn.close()

            return {
                'total_users': total_users,
                'active_users': active_users,
                'feedback_stats': feedback_stats.to_dict('records'),
                'signal_stats': signal_stats.to_dict('records')[0] if not signal_stats.empty else {},
                'engagement_stats': engagement_stats.to_dict('records')
            }

        except Exception as e:
            logger.error(f"Get analytics error: {e}")
            return {}

    def send_welcome_email(self, email: str, name: str, beta_code: str):
        """Send welcome email to new beta user"""
        # Placeholder for email sending
        # In production, integrate with actual email service
        logger.info(f"Welcome email sent to {email} with beta code {beta_code}")

# Streamlit Beta User Interface
class BetaUserInterface:
    def __init__(self):
        self.user_manager = BetaUserManager()

    def render_beta_registration(self):
        """Render beta user registration form"""
        st.markdown("## 🧪 Beta Testing Program Registration")
        st.markdown("Join our exclusive beta testing program for the Vietnam Stock Analysis System!")

        with st.form("beta_registration"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Full Name*")
                email = st.text_input("Email Address*")
                password = st.text_input("Password*", type="password")

            with col2:
                role = st.selectbox("Role*", [
                    "Individual Trader",
                    "Investment Advisor",
                    "Fund Manager",
                    "Financial Analyst",
                    "Other Professional"
                ])

                experience = st.selectbox("Vietnamese Stock Market Experience*", [
                    "Beginner (< 1 year)",
                    "Intermediate (1-3 years)",
                    "Expert (3+ years)"
                ])

                portfolio_size = st.selectbox("Approximate Portfolio Size*", [
                    "Small (< $10,000)",
                    "Medium ($10,000 - $100,000)",
                    "Large (> $100,000)"
                ])

            referral_code = st.text_input("Referral Code (Optional)")

            st.markdown("### Commitment Requirements:")
            commitment = st.checkbox("I commit to actively test the system for 6-8 weeks")
            feedback_commitment = st.checkbox("I will provide regular feedback and report bugs")
            privacy_agreement = st.checkbox("I agree to the beta testing privacy terms")

            submitted = st.form_submit_button("Apply for Beta Access")

            if submitted:
                if not all([name, email, password, commitment, feedback_commitment, privacy_agreement]):
                    st.error("Please fill all required fields and accept commitments")
                else:
                    result = self.user_manager.register_beta_user(
                        email, name, password, role, experience, portfolio_size, referral_code
                    )

                    if result['success']:
                        st.success(result['message'])
                        st.info(f"Your beta access code: `{result['beta_code']}`")
                        st.balloons()
                    else:
                        st.error(result['error'])

    def render_beta_login(self):
        """Render beta user login"""
        st.markdown("## 🔐 Beta User Login")

        with st.form("beta_login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")

            if submitted:
                result = self.user_manager.authenticate_user(email, password)
                if result['success']:
                    st.session_state.beta_user_id = result['user_id']
                    st.session_state.beta_user_name = result['name']
                    st.success(f"Welcome back, {result['name']}!")
                    st.rerun()
                else:
                    st.error(result['error'])

    def render_beta_dashboard(self, user_id: str):
        """Render beta user dashboard"""
        user_profile = self.user_manager.get_user_profile(user_id)
        if not user_profile:
            st.error("User profile not found")
            return

        st.markdown(f"## 🧪 Beta Dashboard - Welcome {user_profile.name}!")

        # Beta stats
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Days in Beta", (datetime.now() - user_profile.signup_date).days)
        with col2:
            st.metric("Feedback Submitted", user_profile.feedback_count)
        with col3:
            st.metric("Signals Tracked", user_profile.signals_tracked)
        with col4:
            st.metric("Beta Level", "Active")

        # Quick feedback
        with st.expander("📝 Quick Feedback"):
            feedback_type = st.selectbox("Type", ["General", "Bug Report", "Feature Request", "Signal Accuracy"])
            feedback_text = st.text_area("Your feedback:")
            rating = st.slider("Rating (1-10)", 1, 10, 7)

            if st.button("Submit Feedback"):
                if self.user_manager.submit_feedback(user_id, feedback_type, feedback_text, rating):
                    st.success("Feedback submitted! Thank you.")
                else:
                    st.error("Failed to submit feedback")

        # Signal tracking
        with st.expander("📊 Track Signal Performance"):
            col1, col2 = st.columns(2)

            with col1:
                symbol = st.text_input("Stock Symbol (e.g., VCB)")
                predicted_action = st.selectbox("Predicted Action", ["BUY", "SELL", "HOLD"])
                predicted_score = st.number_input("Signal Score", 0.0, 100.0, 70.0)

            with col2:
                actual_outcome = st.selectbox("Actual Outcome", ["", "Profitable", "Loss", "Neutral"])
                actual_return = st.number_input("Actual Return %", -50.0, 50.0, 0.0)
                notes = st.text_area("Notes:")

            if st.button("Track Signal"):
                if symbol and predicted_action:
                    if self.user_manager.track_signal_performance(
                        user_id, symbol, datetime.now().strftime('%Y-%m-%d'),
                        predicted_action, predicted_score, actual_outcome, actual_return, notes
                    ):
                        st.success("Signal performance tracked!")
                    else:
                        st.error("Failed to track signal")

    def render_beta_analytics_admin(self):
        """Render beta analytics for admin"""
        st.markdown("## 📊 Beta Program Analytics")

        analytics = self.user_manager.get_beta_analytics()

        if analytics:
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Beta Users", analytics['total_users'])
            with col2:
                st.metric("Active Users", analytics['active_users'])
            with col3:
                if analytics['signal_stats']:
                    accuracy = analytics['signal_stats'].get('avg_accuracy', 0)
                    st.metric("Average Signal Accuracy", f"{accuracy*100:.1f}%" if accuracy else "N/A")

            # Feedback analysis
            if analytics['feedback_stats']:
                st.markdown("### Feedback Statistics")
                feedback_df = pd.DataFrame(analytics['feedback_stats'])
                fig = px.bar(feedback_df, x='feedback_type', y='count', title='Feedback by Type')
                st.plotly_chart(fig, use_container_width=True)

            # User engagement
            if analytics['engagement_stats']:
                st.markdown("### User Engagement (Last 7 Days)")
                engagement_df = pd.DataFrame(analytics['engagement_stats'])
                fig = px.line(engagement_df, x='date', y='active_users', title='Daily Active Users')
                st.plotly_chart(fig, use_container_width=True)

def main():
    """Main beta user interface"""
    beta_ui = BetaUserInterface()

    # Initialize session state
    if 'beta_user_id' not in st.session_state:
        st.session_state.beta_user_id = None

    # Navigation
    if st.session_state.beta_user_id:
        # Logged in user
        tab1, tab2, tab3 = st.tabs(["Dashboard", "Analytics", "Logout"])

        with tab1:
            beta_ui.render_beta_dashboard(st.session_state.beta_user_id)

        with tab2:
            # Admin analytics (for now, show to all beta users)
            beta_ui.render_beta_analytics_admin()

        with tab3:
            if st.button("Logout"):
                st.session_state.beta_user_id = None
                st.rerun()
    else:
        # Not logged in
        tab1, tab2 = st.tabs(["Login", "Register"])

        with tab1:
            beta_ui.render_beta_login()

        with tab2:
            beta_ui.render_beta_registration()

if __name__ == "__main__":
    main()