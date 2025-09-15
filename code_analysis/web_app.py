#!/usr/bin/env python3
"""
Vietnam Stock Analysis Web Application
Streamlit-based dashboard for comprehensive stock analysis system
Deploy-ready with all analysis features
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import logging
from typing import Dict, List

# Import our analysis systems
try:
    from comprehensive_stock_reporter import ComprehensiveStockReporter
    from smart_money_signal_system import SmartMoneySignalSystem
    from eic_framework import EICFramework
    from market_maker_analyzer import MarketMakerAnalyzer
    from stock_universe_manager import VietnamStockUniverse
except ImportError as e:
    st.error(f"Import error: {e}. Please ensure all analysis modules are available.")

# Configure logging
logging.basicConfig(level=logging.INFO)

class VietnamStockAnalysisApp:
    def __init__(self):
        # Initialize all analysis systems
        try:
            self.reporter = ComprehensiveStockReporter()
            self.signal_system = SmartMoneySignalSystem()
            self.eic_framework = EICFramework()
            self.mm_analyzer = MarketMakerAnalyzer()
            self.universe_manager = VietnamStockUniverse()
        except Exception as e:
            st.error(f"Failed to initialize analysis systems: {e}")

        # Popular Vietnam stocks for quick access
        self.popular_stocks = [
            'VCB', 'BID', 'CTG', 'TCB', 'MBB', 'VPB', 'TPB', 'STB',  # Banks
            'VIC', 'VHM', 'NVL', 'DXG', 'KDH', 'HDG',                # Real Estate
            'FPT', 'CMG', 'ELC', 'ITD',                              # Technology
            'HPG', 'HSG', 'NKG', 'SMC',                              # Steel
            'VNM', 'MSN', 'MCH', 'KDC',                              # F&B
            'GAS', 'PLX', 'PVS', 'PVD',                              # Oil & Gas
            'MWG', 'PNJ', 'DGW', 'FRT',                              # Retail
            'HVN', 'VJC'                                             # Airlines
        ]

    def run(self):
        """Run the Streamlit application"""
        st.set_page_config(
            page_title="Vietnam Stock Analysis System",
            page_icon="📈",
            layout="wide",
            initial_sidebar_state="expanded"
        )

        # Custom CSS
        st.markdown("""
        <style>
        .main-header {
            font-size: 2.5rem;
            color: #1e3d59;
            text-align: center;
            margin-bottom: 2rem;
        }
        .metric-card {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid #1e3d59;
        }
        .signal-strong-buy {
            background-color: #d4edda;
            color: #155724;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-weight: bold;
        }
        .signal-buy {
            background-color: #cce5ff;
            color: #004085;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-weight: bold;
        }
        .signal-sell {
            background-color: #f8d7da;
            color: #721c24;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        # Header
        st.markdown('<h1 class="main-header">🇻🇳 Vietnam Stock Analysis System</h1>', unsafe_allow_html=True)
        st.markdown("### Deep insights with smart money tracking and EIC analysis")

        # Sidebar navigation
        with st.sidebar:
            st.image("https://via.placeholder.com/200x80/1e3d59/ffffff?text=Vietnam+Stocks", width=200)

            analysis_type = st.selectbox(
                "Choose Analysis Type",
                [
                    "📊 Comprehensive Analysis",
                    "🎯 Smart Money Signals",
                    "🏢 EIC Framework",
                    "💹 Market Maker Analysis",
                    "🌏 Stock Universe",
                    "📈 Multi-Stock Comparison"
                ]
            )

            # Stock selection
            st.subheader("Stock Selection")

            input_method = st.radio(
                "Select method:",
                ["Popular Stocks", "Manual Input"]
            )

            if input_method == "Popular Stocks":
                selected_symbol = st.selectbox(
                    "Choose a stock:",
                    self.popular_stocks,
                    help="Select from popular Vietnam stocks"
                )
            else:
                selected_symbol = st.text_input(
                    "Enter stock symbol:",
                    value="VCB",
                    help="Enter Vietnam stock symbol (e.g., VCB, FPT, VIC)"
                ).upper()

            if st.button("🚀 Analyze Stock", type="primary"):
                st.session_state.analyze_stock = True
                st.session_state.selected_symbol = selected_symbol

        # Main content area
        if hasattr(st.session_state, 'analyze_stock') and st.session_state.analyze_stock:
            symbol = st.session_state.selected_symbol

            if analysis_type == "📊 Comprehensive Analysis":
                self.show_comprehensive_analysis(symbol)
            elif analysis_type == "🎯 Smart Money Signals":
                self.show_smart_money_signals(symbol)
            elif analysis_type == "🏢 EIC Framework":
                self.show_eic_analysis(symbol)
            elif analysis_type == "💹 Market Maker Analysis":
                self.show_market_maker_analysis(symbol)
            elif analysis_type == "🌏 Stock Universe":
                self.show_stock_universe()
            elif analysis_type == "📈 Multi-Stock Comparison":
                self.show_multi_stock_comparison()

        else:
            self.show_welcome_screen()

    def show_welcome_screen(self):
        """Show welcome screen with system overview"""

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("""
            ### 🎯 Smart Money Tracking
            - Detect institutional trading patterns
            - Volume analysis and flow direction
            - Entry/exit signals with precise levels
            - Risk management parameters
            """)

        with col2:
            st.markdown("""
            ### 🏢 EIC Framework
            - Environment analysis
            - Infrastructure assessment
            - Competitiveness evaluation
            - Top-down investment approach
            """)

        with col3:
            st.markdown("""
            ### 💹 Market Maker Analysis
            - Market maker behavior patterns
            - Liquidity provision quality
            - Price discovery efficiency
            - Institutional activity detection
            """)

        st.markdown("---")

        # System statistics
        st.subheader("📈 System Capabilities")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Stocks Covered", "500+", help="All liquid Vietnamese stocks")
        with col2:
            st.metric("Analysis Types", "6", help="Comprehensive analysis modules")
        with col3:
            st.metric("Technical Indicators", "25+", help="Advanced technical analysis")
        with col4:
            st.metric("Update Frequency", "Daily", help="Real-time market data")

        # Quick start instructions
        st.markdown("---")
        st.subheader("🚀 Quick Start")
        st.markdown("""
        1. **Select Analysis Type** from the sidebar
        2. **Choose a Stock** from popular stocks or enter manually
        3. **Click Analyze** to generate comprehensive insights
        4. **Review Results** including signals, risks, and recommendations
        """)

        # Sample analysis preview
        with st.expander("📊 See Sample Analysis Preview"):
            st.markdown("""
            #### Sample: VCB Analysis Preview
            - **Composite Score**: 78.5/100 (Strong Buy)
            - **Smart Money Flow**: Moderate Inflow
            - **EIC Score**: 72.3 (EIC-A)
            - **Market Maker Activity**: Professional Market Maker
            - **Risk Level**: Medium (B Grade)
            """)

    def show_comprehensive_analysis(self, symbol: str):
        """Show comprehensive analysis dashboard"""

        st.subheader(f"📊 Comprehensive Analysis: {symbol}")

        with st.spinner(f"Generating comprehensive analysis for {symbol}..."):
            try:
                # Get sector classification
                sector = self.universe_manager.classify_stock_sector(symbol)

                # Generate comprehensive report
                report = self.reporter.generate_comprehensive_report(symbol, sector)

                if 'error' in report:
                    st.error(f"Error analyzing {symbol}: {report['error']}")
                    return

                # Display key metrics at the top
                self.display_key_metrics(report)

                # Create tabs for different analysis sections
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📈 Executive Summary",
                    "🔍 Technical Analysis",
                    "🏢 EIC Analysis",
                    "💹 Market Maker",
                    "⚠️ Risk Assessment"
                ])

                with tab1:
                    self.display_executive_summary(report)

                with tab2:
                    self.display_technical_analysis(report)

                with tab3:
                    self.display_eic_analysis(report)

                with tab4:
                    self.display_market_maker_analysis(report)

                with tab5:
                    self.display_risk_assessment(report)

            except Exception as e:
                st.error(f"Error generating analysis: {e}")
                logging.error(f"Comprehensive analysis error: {e}")

    def display_key_metrics(self, report: Dict):
        """Display key metrics in a dashboard format"""

        # Extract key scores
        composite_score = report.get('composite_score', {}).get('composite_score', 50)
        investment_grade = report.get('composite_score', {}).get('investment_grade', 'B - Hold')

        # Create columns for metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Composite Score",
                f"{composite_score:.1f}/100",
                delta=f"{composite_score - 50:.1f}" if composite_score != 50 else None,
                help="Overall investment attractiveness score"
            )

        with col2:
            # Extract smart money flow
            smart_money = report.get('market_maker_analysis', {}).get('smart_money_analysis', {})
            flow_direction = smart_money.get('flow_direction', 'Neutral')
            st.metric(
                "Smart Money Flow",
                flow_direction,
                help="Direction of institutional money flow"
            )

        with col3:
            # Extract EIC score
            eic_score = report.get('eic_analysis', {}).get('eic_score', 50)
            st.metric(
                "EIC Score",
                f"{eic_score:.1f}/100",
                delta=f"{eic_score - 50:.1f}" if eic_score != 50 else None,
                help="Environment-Infrastructure-Competitiveness score"
            )

        with col4:
            # Extract operations score
            ops_score = report.get('company_operations', {}).get('operations_score', 50)
            st.metric(
                "Operations Score",
                f"{ops_score:.1f}/100",
                delta=f"{ops_score - 50:.1f}" if ops_score != 50 else None,
                help="Company operational performance score"
            )

        # Investment recommendation
        st.markdown("---")
        recommendation = report.get('executive_summary', {}).get('recommended_action', 'Hold')

        if 'Strong Buy' in recommendation:
            st.markdown(f'<div class="signal-strong-buy">🎯 {recommendation}</div>', unsafe_allow_html=True)
        elif 'Buy' in recommendation:
            st.markdown(f'<div class="signal-buy">📈 {recommendation}</div>', unsafe_allow_html=True)
        elif 'Sell' in recommendation:
            st.markdown(f'<div class="signal-sell">📉 {recommendation}</div>', unsafe_allow_html=True)
        else:
            st.info(f"📊 {recommendation}")

    def display_executive_summary(self, report: Dict):
        """Display executive summary section"""

        summary = report.get('executive_summary', {})

        # Investment thesis
        st.markdown("### 🎯 Investment Thesis")
        st.markdown(summary.get('investment_thesis', 'No thesis available'))

        col1, col2 = st.columns(2)

        with col1:
            # Key insights
            st.markdown("#### ✅ Key Insights")
            insights = summary.get('key_insights', [])
            for insight in insights:
                st.markdown(f"• {insight}")

            # Primary catalysts
            st.markdown("#### 🚀 Primary Catalysts")
            catalysts = summary.get('primary_catalysts', [])
            for catalyst in catalysts:
                st.markdown(f"• {catalyst}")

        with col2:
            # Key risks
            st.markdown("#### ⚠️ Key Risks")
            risks = summary.get('key_risks', [])
            for risk in risks:
                st.markdown(f"• {risk}")

            # Investment details
            st.markdown("#### 📊 Investment Details")
            st.markdown(f"**Time Horizon**: {summary.get('time_horizon', 'Medium-term')}")
            st.markdown(f"**Confidence Level**: {summary.get('confidence_level', 'Medium')}")

    def display_technical_analysis(self, report: Dict):
        """Display technical analysis section"""

        technical = report.get('technical_analysis', {})

        if 'pattern_analysis' in technical:
            pattern_analysis = technical['pattern_analysis']

            # Price metrics
            st.markdown("### 📈 Price Metrics")
            price_metrics = pattern_analysis.get('price_metrics', {})

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Price", f"{price_metrics.get('current_price', 0):,.0f} VND")
            with col2:
                st.metric("52W High", f"{price_metrics.get('52_week_high', 0):,.0f} VND")
            with col3:
                st.metric("52W Low", f"{price_metrics.get('52_week_low', 0):,.0f} VND")

            # Position in range
            position = price_metrics.get('position_in_range', 50)
            st.markdown(f"**Position in 52W Range**: {position:.1f}%")

            # Progress bar for position
            progress_color = "green" if position > 70 else "orange" if position > 30 else "red"
            st.progress(position/100)

            # Performance metrics
            st.markdown("### 📊 Performance Metrics")
            performance = pattern_analysis.get('performance', {})

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("52W Return", f"{performance.get('total_return_52w', 0):.1f}%")
            with col2:
                st.metric("Volatility", f"{performance.get('annualized_volatility', 0):.1f}%")
            with col3:
                st.metric("Sharpe Ratio", f"{performance.get('sharpe_ratio', 0):.2f}")
            with col4:
                st.metric("Max Drawdown", f"{performance.get('max_drawdown', 0):.1f}%")

    def display_eic_analysis(self, report: Dict):
        """Display EIC analysis section"""

        eic = report.get('eic_analysis', {})

        # EIC score breakdown
        st.markdown("### 🏢 EIC Score Breakdown")

        component_scores = eic.get('component_scores', {})

        # Create a radar chart for EIC components
        if component_scores:
            categories = []
            values = []

            if 'environment' in component_scores:
                categories.append('Environment')
                values.append(component_scores['environment'].get('environment_score', 50))

            if 'infrastructure' in component_scores:
                categories.append('Infrastructure')
                values.append(component_scores['infrastructure'].get('infrastructure_score', 50))

            if 'competitiveness' in component_scores:
                categories.append('Competitiveness')
                values.append(component_scores['competitiveness'].get('competitiveness_score', 50))

            if categories and values:
                # Create radar chart
                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='EIC Scores'
                ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100]
                        )),
                    showlegend=True,
                    title="EIC Component Analysis"
                )

                st.plotly_chart(fig, use_container_width=True)

        # Executive summary
        executive_summary = eic.get('executive_summary', {})
        if executive_summary:
            st.markdown("#### 📋 EIC Executive Summary")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**Strengths:**")
                for strength in executive_summary.get('key_strengths', []):
                    st.markdown(f"• {strength}")

            with col2:
                st.markdown("**Weaknesses:**")
                for weakness in executive_summary.get('key_weaknesses', []):
                    st.markdown(f"• {weakness}")

    def display_market_maker_analysis(self, report: Dict):
        """Display market maker analysis section"""

        mm = report.get('market_maker_analysis', {})

        # Market maker style
        if 'market_maker_style' in mm:
            mm_style = mm['market_maker_style']

            st.markdown("### 💹 Market Maker Profile")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Style**: {mm_style.get('style_classification', 'Unknown')}")
                st.markdown(f"**Aggression Level**: {mm_style.get('aggression_level', 'Unknown')}")
                st.markdown(f"**Efficiency Score**: {mm_style.get('efficiency_score', 0):.1f}/100")

            with col2:
                characteristics = mm_style.get('characteristics', [])
                st.markdown("**Characteristics:**")
                for char in characteristics:
                    st.markdown(f"• {char}")

        # Current market phase
        if 'current_market_phase' in mm:
            phase = mm['current_market_phase']

            st.markdown("### 📊 Current Market Phase")
            st.markdown(f"**Phase**: {phase.get('current_phase', 'Unknown')}")
            st.markdown(f"**Expected MM Behavior**: {phase.get('mm_expected_behavior', 'Unknown')}")

            # Phase characteristics
            characteristics = phase.get('phase_characteristics', [])
            if characteristics:
                st.markdown("**Phase Characteristics:**")
                for char in characteristics:
                    st.markdown(f"• {char}")

        # Smart money analysis
        if 'smart_money_analysis' in mm:
            smart_money = mm['smart_money_analysis']

            st.markdown("### 🧠 Smart Money Analysis")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Smart Money Score", f"{smart_money.get('smart_money_score', 50):.1f}/100")
            with col2:
                st.metric("Flow Direction", smart_money.get('flow_direction', 'Neutral'))
            with col3:
                st.metric("Confidence Level", smart_money.get('confidence_level', 'Medium'))

    def display_risk_assessment(self, report: Dict):
        """Display risk assessment section"""

        risk = report.get('risk_assessment', {})

        st.markdown("### ⚠️ Risk Assessment")

        # Overall risk metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Overall Risk Level", risk.get('overall_risk_level', 'Medium'))
        with col2:
            st.metric("Risk Score", f"{risk.get('risk_score', 50):.0f}/100")
        with col3:
            # Time sensitive factors
            time_sensitive = report.get('time_sensitive_factors', {})
            urgent_count = len(time_sensitive.get('urgent_factors', []))
            st.metric("Urgent Factors", urgent_count)

        # Risk categories
        st.markdown("#### Risk Breakdown")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Technical Risks:**")
            for risk_item in risk.get('technical_risks', []):
                st.markdown(f"• {risk_item}")

            st.markdown("**Fundamental Risks:**")
            for risk_item in risk.get('fundamental_risks', []):
                st.markdown(f"• {risk_item}")

        with col2:
            st.markdown("**Market Structure Risks:**")
            for risk_item in risk.get('market_structure_risks', []):
                st.markdown(f"• {risk_item}")

        # Time sensitive factors
        time_sensitive = report.get('time_sensitive_factors', {})
        if time_sensitive.get('urgent_factors'):
            st.markdown("#### 🚨 Urgent Attention Required")
            for factor in time_sensitive['urgent_factors']:
                st.warning(factor)

    def show_smart_money_signals(self, symbol: str):
        """Show smart money signals dashboard"""

        st.subheader(f"🎯 Smart Money Signals: {symbol}")

        with st.spinner(f"Generating smart money signals for {symbol}..."):
            try:
                signals = self.signal_system.generate_smart_money_signals(symbol)

                if 'error' in signals:
                    st.error(f"Error generating signals for {symbol}: {signals['error']}")
                    return

                # Display composite signal score
                composite = signals.get('composite_signal_score', {})

                st.markdown("### 📊 Signal Dashboard")

                col1, col2, col3 = st.columns(3)

                with col1:
                    score = composite.get('composite_score', 50)
                    st.metric("Composite Signal", f"{score:.1f}/100")

                with col2:
                    classification = composite.get('signal_classification', 'Hold Signal')
                    st.metric("Classification", classification)

                with col3:
                    strength = composite.get('signal_strength', 'Moderate')
                    st.metric("Signal Strength", strength)

                # Signal components breakdown
                st.markdown("### 🔍 Signal Components")

                component_scores = composite.get('component_scores', {})

                # Create bar chart for component scores
                if component_scores:
                    components = list(component_scores.keys())
                    scores = list(component_scores.values())

                    fig = px.bar(
                        x=scores,
                        y=components,
                        orientation='h',
                        title='Signal Component Breakdown',
                        color=scores,
                        color_continuous_scale='RdYlGn'
                    )
                    fig.update_layout(showlegend=False)
                    st.plotly_chart(fig, use_container_width=True)

                # Entry/Exit signals
                entry_exit = signals.get('entry_exit_signals', {})

                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("#### 📈 Entry Signals")
                    entry_signals = entry_exit.get('entry_signals', [])

                    if entry_signals:
                        for signal in entry_signals:
                            with st.expander(f"🎯 {signal.get('type', 'Signal').replace('_', ' ').title()}"):
                                st.markdown(f"**Entry Price**: {signal.get('entry_price', 'N/A')}")
                                st.markdown(f"**Reasoning**: {signal.get('reasoning', 'N/A')}")
                                st.markdown(f"**Urgency**: {signal.get('urgency', 'Medium')}")
                    else:
                        st.info("No specific entry signals at current levels")

                with col2:
                    st.markdown("#### 📉 Risk Management")

                    # Stop loss levels
                    stop_losses = entry_exit.get('stop_loss_levels', {})
                    if stop_losses:
                        st.markdown("**Stop Loss Levels:**")
                        for level_type, price in stop_losses.items():
                            st.markdown(f"• {level_type.title()}: {price:.2f}")

                    # Target levels
                    targets = entry_exit.get('target_levels', {})
                    if targets:
                        st.markdown("**Target Levels:**")
                        for target, price in targets.items():
                            st.markdown(f"• {target.replace('_', ' ').title()}: {price:.2f}")

                # Risk management
                risk_mgmt = signals.get('risk_management', {})
                if risk_mgmt:
                    st.markdown("### ⚠️ Risk Management")

                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.metric("Risk Grade", risk_mgmt.get('risk_grade', 'C - Medium Risk'))
                    with col2:
                        vol_metrics = risk_mgmt.get('volatility_metrics', {})
                        st.metric("Annualized Volatility", f"{vol_metrics.get('annualized_volatility', 0):.1f}%")
                    with col3:
                        st.metric("Max Drawdown", f"{vol_metrics.get('maximum_drawdown', 0):.1f}%")

                # Actionable recommendations
                recommendations = signals.get('actionable_recommendations', {})
                if recommendations:
                    st.markdown("### 💡 Actionable Recommendations")

                    # Immediate actions
                    immediate = recommendations.get('immediate_actions', [])
                    if immediate:
                        st.markdown("#### 🚨 Immediate Actions")
                        for action in immediate:
                            st.markdown(f"• {action}")

                    # Risk management recommendations
                    risk_actions = recommendations.get('risk_management', [])
                    if risk_actions:
                        st.markdown("#### 🛡️ Risk Management")
                        for action in risk_actions:
                            st.markdown(f"• {action}")

            except Exception as e:
                st.error(f"Error generating smart money signals: {e}")
                logging.error(f"Smart money signals error: {e}")

    def show_eic_analysis(self, symbol: str):
        """Show EIC framework analysis"""

        st.subheader(f"🏢 EIC Framework Analysis: {symbol}")

        with st.spinner(f"Running EIC analysis for {symbol}..."):
            try:
                sector = self.universe_manager.classify_stock_sector(symbol)
                eic_analysis = self.eic_framework.calculate_comprehensive_eic_score(symbol, sector)

                if 'error' in eic_analysis:
                    st.error(f"Error in EIC analysis for {symbol}: {eic_analysis['error']}")
                    return

                # Main EIC score
                st.markdown("### 🎯 EIC Score Overview")

                col1, col2, col3 = st.columns(3)

                with col1:
                    eic_score = eic_analysis.get('eic_score', 50)
                    st.metric("EIC Score", f"{eic_score:.1f}/100")

                with col2:
                    grade = eic_analysis.get('investment_grade', 'B - Average')
                    st.metric("Investment Grade", grade)

                with col3:
                    st.metric("Sector", sector.replace('_', ' '))

                # Component analysis
                st.markdown("### 📊 Component Analysis")

                components = eic_analysis.get('component_scores', {})

                if components:
                    # Create tabs for each component
                    env_tab, infra_tab, comp_tab = st.tabs(["🌍 Environment", "🏗️ Infrastructure", "🏆 Competitiveness"])

                    with env_tab:
                        env_data = components.get('environment', {})
                        score = env_data.get('environment_score', 50)
                        st.metric("Environment Score", f"{score:.1f}/100")
                        st.markdown(env_data.get('analysis', 'No analysis available'))

                    with infra_tab:
                        infra_data = components.get('infrastructure', {})
                        score = infra_data.get('infrastructure_score', 50)
                        st.metric("Infrastructure Score", f"{score:.1f}/100")
                        st.markdown(infra_data.get('analysis', 'No analysis available'))

                    with comp_tab:
                        comp_data = components.get('competitiveness', {})
                        score = comp_data.get('competitiveness_score', 50)
                        st.metric("Competitiveness Score", f"{score:.1f}/100")
                        st.markdown(comp_data.get('analysis', 'No analysis available'))

                # Executive summary
                exec_summary = eic_analysis.get('executive_summary', {})
                if exec_summary:
                    st.markdown("### 📋 Executive Summary")

                    st.markdown(f"**Assessment**: {exec_summary.get('overall_assessment', 'No assessment')}")
                    st.markdown(f"**Recommendation**: {exec_summary.get('recommendation', 'Hold')}")
                    st.markdown(f"**Risk Level**: {exec_summary.get('risk_level', 'Medium')}")

                    col1, col2 = st.columns(2)

                    with col1:
                        strengths = exec_summary.get('key_strengths', [])
                        if strengths:
                            st.markdown("**Key Strengths:**")
                            for strength in strengths:
                                st.markdown(f"• {strength}")

                    with col2:
                        weaknesses = exec_summary.get('key_weaknesses', [])
                        if weaknesses:
                            st.markdown("**Key Weaknesses:**")
                            for weakness in weaknesses:
                                st.markdown(f"• {weakness}")

            except Exception as e:
                st.error(f"Error in EIC analysis: {e}")
                logging.error(f"EIC analysis error: {e}")

    def show_market_maker_analysis(self, symbol: str):
        """Show market maker analysis"""

        st.subheader(f"💹 Market Maker Analysis: {symbol}")

        with st.spinner(f"Analyzing market maker behavior for {symbol}..."):
            try:
                mm_analysis = self.mm_analyzer.analyze_market_maker_style(symbol)

                if 'error' in mm_analysis:
                    st.error(f"Error in market maker analysis for {symbol}: {mm_analysis['error']}")
                    return

                # Market maker style overview
                mm_style = mm_analysis.get('market_maker_style', {})

                st.markdown("### 🎭 Market Maker Profile")

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Style", mm_style.get('style_classification', 'Unknown'))

                with col2:
                    st.metric("Aggression", mm_style.get('aggression_level', 'Unknown'))

                with col3:
                    efficiency = mm_style.get('efficiency_score', 0)
                    st.metric("Efficiency Score", f"{efficiency:.1f}/100")

                # Current market phase
                phase = mm_analysis.get('current_market_phase', {})

                st.markdown("### 📊 Current Market Phase")
                st.info(f"**Phase**: {phase.get('current_phase', 'Unknown')}")
                st.markdown(f"**Expected Behavior**: {phase.get('mm_expected_behavior', 'Unknown')}")

                # Smart money flow
                smart_money = mm_analysis.get('smart_money_analysis', {})

                st.markdown("### 🧠 Smart Money Flow")

                col1, col2, col3 = st.columns(3)

                with col1:
                    score = smart_money.get('smart_money_score', 50)
                    st.metric("Smart Money Score", f"{score:.1f}/100")

                with col2:
                    flow = smart_money.get('flow_direction', 'Neutral')
                    st.metric("Flow Direction", flow)

                with col3:
                    confidence = smart_money.get('confidence_level', 'Medium')
                    st.metric("Confidence", confidence)

                # Actionable insights
                insights = mm_analysis.get('actionable_insights', {})
                if insights:
                    st.markdown("### 💡 Actionable Insights")

                    opportunity = insights.get('primary_opportunity', '')
                    if opportunity:
                        st.success(f"**Primary Opportunity**: {opportunity}")

                    # Risk considerations
                    risks = insights.get('risk_considerations', [])
                    if risks:
                        st.markdown("**Risk Considerations:**")
                        for risk in risks:
                            st.warning(f"• {risk}")

                    # Timing factors
                    timing = insights.get('timing_factors', [])
                    if timing:
                        st.markdown("**Timing Factors:**")
                        for factor in timing:
                            st.info(f"• {factor}")

                # Entry/Exit signals from MM analysis
                mm_signals = mm_analysis.get('entry_exit_signals', {})
                if mm_signals:
                    st.markdown("### 📈 Trading Signals")

                    col1, col2 = st.columns(2)

                    with col1:
                        entry_signals = mm_signals.get('entry_signals', [])
                        if entry_signals:
                            st.markdown("**Entry Signals:**")
                            for signal in entry_signals:
                                st.markdown(f"• **{signal.get('signal', 'Signal')}**: {signal.get('trigger', 'N/A')} ({signal.get('strength', 'Medium')})")

                    with col2:
                        exit_signals = mm_signals.get('exit_signals', [])
                        if exit_signals:
                            st.markdown("**Exit Signals:**")
                            for signal in exit_signals:
                                st.markdown(f"• **{signal.get('signal', 'Signal')}**: {signal.get('trigger', 'N/A')}")

                        # Stop loss and targets
                        stop_loss = mm_signals.get('stop_loss_level', 0)
                        if stop_loss:
                            st.markdown(f"**Stop Loss**: {stop_loss:.2f}")

                        targets = mm_signals.get('target_levels', [])
                        if targets:
                            st.markdown("**Targets:**")
                            for i, target in enumerate(targets, 1):
                                st.markdown(f"• Target {i}: {target:.2f}")

            except Exception as e:
                st.error(f"Error in market maker analysis: {e}")
                logging.error(f"Market maker analysis error: {e}")

    def show_stock_universe(self):
        """Show stock universe overview"""

        st.subheader("🌏 Vietnam Stock Universe")
        st.markdown("Overview of liquid Vietnamese stocks by sector")

        with st.spinner("Loading stock universe data..."):
            try:
                # This would load from a saved universe file in production
                st.info("Stock universe data would be loaded from the most recent universe build")

                # Sample sector breakdown
                sector_data = {
                    'Banks': 15,
                    'Real Estate': 12,
                    'Technology': 8,
                    'Steel': 9,
                    'Food & Beverage': 10,
                    'Oil & Gas': 9,
                    'Retail': 8,
                    'Healthcare': 6,
                    'Manufacturing': 15,
                    'Other': 18
                }

                # Create pie chart
                fig = px.pie(
                    values=list(sector_data.values()),
                    names=list(sector_data.keys()),
                    title="Stock Distribution by Sector"
                )
                st.plotly_chart(fig, use_container_width=True)

                # Sector details
                st.markdown("### 📊 Sector Breakdown")

                for sector, count in sector_data.items():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{sector}**")
                    with col2:
                        st.markdown(f"{count} stocks")

                # Top stocks by liquidity (sample)
                st.markdown("### 🚀 Top Liquid Stocks")

                sample_stocks = [
                    {'Symbol': 'VCB', 'Sector': 'Banks', 'Liquidity Score': 95.2, 'Volume': '2,450,000'},
                    {'Symbol': 'VIC', 'Sector': 'Real Estate', 'Liquidity Score': 92.8, 'Volume': '1,890,000'},
                    {'Symbol': 'FPT', 'Sector': 'Technology', 'Liquidity Score': 89.5, 'Volume': '1,560,000'},
                    {'Symbol': 'HPG', 'Sector': 'Steel', 'Liquidity Score': 87.3, 'Volume': '1,430,000'},
                    {'Symbol': 'GAS', 'Sector': 'Oil & Gas', 'Liquidity Score': 85.9, 'Volume': '1,320,000'}
                ]

                df = pd.DataFrame(sample_stocks)
                st.dataframe(df, use_container_width=True)

            except Exception as e:
                st.error(f"Error loading stock universe: {e}")

    def show_multi_stock_comparison(self):
        """Show multi-stock comparison"""

        st.subheader("📈 Multi-Stock Comparison")

        # Stock selection for comparison
        selected_stocks = st.multiselect(
            "Select stocks to compare (2-5 stocks):",
            self.popular_stocks,
            default=['VCB', 'FPT', 'VIC'],
            max_selections=5,
            help="Select 2-5 stocks for comparison"
        )

        if len(selected_stocks) >= 2:
            if st.button("🔍 Compare Stocks", type="primary"):
                with st.spinner("Comparing selected stocks..."):
                    try:
                        # This would run comparison analysis
                        st.info("Multi-stock comparison would analyze all selected stocks and provide relative rankings")

                        # Sample comparison data
                        comparison_data = []
                        for symbol in selected_stocks:
                            # In production, would call actual analysis
                            comparison_data.append({
                                'Symbol': symbol,
                                'Composite Score': np.random.uniform(45, 85),
                                'Smart Money': np.random.choice(['Inflow', 'Outflow', 'Neutral']),
                                'EIC Score': np.random.uniform(40, 80),
                                'Risk Level': np.random.choice(['Low', 'Medium', 'High'])
                            })

                        df = pd.DataFrame(comparison_data)
                        df = df.sort_values('Composite Score', ascending=False)

                        st.markdown("### 🏆 Comparison Results")
                        st.dataframe(df, use_container_width=True)

                        # Visualization
                        fig = px.bar(
                            df,
                            x='Symbol',
                            y='Composite Score',
                            title='Composite Score Comparison',
                            color='Composite Score',
                            color_continuous_scale='RdYlGn'
                        )
                        st.plotly_chart(fig, use_container_width=True)

                    except Exception as e:
                        st.error(f"Error in comparison: {e}")
        else:
            st.info("Please select at least 2 stocks for comparison")

def main():
    """Main function to run the Streamlit app"""
    app = VietnamStockAnalysisApp()
    app.run()

if __name__ == "__main__":
    main()