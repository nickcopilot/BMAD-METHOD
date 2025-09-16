#!/usr/bin/env python3
"""
Beta Monitoring Dashboard
Real-time monitoring for production environment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from beta_monitoring_system import BetaMonitoringSystem

st.set_page_config(
    page_title="Beta Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize monitoring
@st.cache_resource
def init_monitoring():
    return BetaMonitoringSystem()

monitoring = init_monitoring()

st.title("🎯 Beta Testing Monitoring Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
days = st.sidebar.selectbox("Time Period", [1, 7, 14, 30], index=1)
auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)

if auto_refresh:
    st.rerun()

# Get analytics data
analytics = monitoring.get_user_analytics(days=days)
health = monitoring.get_system_health()

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Active Users Today", health.get('active_users_today', 0))

with col2:
    accuracy = health.get('signal_accuracy_today')
    st.metric("Signal Accuracy Today",
             f"{accuracy:.1%}" if accuracy else "No data")

with col3:
    total_signals = analytics.get('signal_performance', {}).get('total_signals', 0)
    st.metric("Total Signals", total_signals)

with col4:
    avg_return = analytics.get('signal_performance', {}).get('avg_return', 0)
    st.metric("Avg Return", f"{avg_return:.2%}" if avg_return else "No data")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Daily Engagement")
    if analytics.get('daily_engagement'):
        df = pd.DataFrame(analytics['daily_engagement'])
        fig = px.line(df, x='date', y='active_users', title='Active Users Over Time')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Feature Usage")
    if analytics.get('feature_usage'):
        df = pd.DataFrame(analytics['feature_usage'])
        fig = px.bar(df, x='feature_name', y='total_usage', title='Most Used Features')
        st.plotly_chart(fig, use_container_width=True)

# System health
st.subheader("System Health")
if health.get('recent_errors'):
    st.warning("Recent errors detected!")
    error_df = pd.DataFrame(health['recent_errors'])
    st.dataframe(error_df)
else:
    st.success("No errors in the last 24 hours")

# Raw data (expandable)
with st.expander("Raw Analytics Data"):
    st.json(analytics)
