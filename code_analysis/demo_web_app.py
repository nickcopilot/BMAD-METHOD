#!/usr/bin/env python3
"""
Demo Vietnam Stock Analysis Web Application
Streamlit-based demo for testing the web interface
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import json

# Mock data for demo purposes
DEMO_ANALYSIS = {
    'BID': {
        'comprehensive_analysis': {
            'composite_score': 54.6,
            'investment_grade': 'B - Hold',
            'recommended_action': 'Hold - Monitor for improvement',
            'time_horizon': 'Medium-term (3-6 months)',
            'confidence_level': 'Medium'
        },
        'eic_analysis': {
            'eic_score': 65.4,
            'eic_grade': 'EIC-B+ (Good)',
            'environment_score': 59.2,
            'infrastructure_score': 65.5,
            'competitiveness_score': 72.6
        },
        'technical_analysis': {
            'current_price': 42.2,
            'week_52_high': 45.1,
            'week_52_low': 31.2,
            'position_in_range': 79.1,
            'annual_return': 6.9,
            'volatility': 24.0,
            'trend': 'Bullish',
            'support': 37.55,
            'resistance': 45.1
        },
        'smart_money': {
            'flow_direction': 'Moderate Inflow',
            'confidence': 'Medium',
            'signals': ['Volume accumulation pattern', 'Institutional buying interest']
        }
    },
    'VCB': {
        'comprehensive_analysis': {
            'composite_score': 78.3,
            'investment_grade': 'A - Buy',
            'recommended_action': 'Buy - Attractive investment opportunity',
            'time_horizon': 'Medium-term (3-6 months)',
            'confidence_level': 'High'
        },
        'eic_analysis': {
            'eic_score': 75.8,
            'eic_grade': 'EIC-A (Strong)',
            'environment_score': 72.1,
            'infrastructure_score': 78.2,
            'competitiveness_score': 77.1
        },
        'technical_analysis': {
            'current_price': 89.5,
            'week_52_high': 92.0,
            'week_52_low': 68.2,
            'position_in_range': 89.5,
            'annual_return': 18.7,
            'volatility': 19.3,
            'trend': 'Strong Bullish',
            'support': 85.2,
            'resistance': 92.0
        },
        'smart_money': {
            'flow_direction': 'Strong Inflow',
            'confidence': 'High',
            'signals': ['Large block accumulation', 'Smart money positioning', 'Institutional interest']
        }
    }
}

class VietnamStockAnalysisDemo:
    def __init__(self):
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
        """Run the Streamlit demo application"""
        st.set_page_config(
            page_title="Vietnam Stock Analysis System - DEMO",
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
        .signal-hold {
            background-color: #fff3cd;
            color: #856404;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)

        # Header
        st.markdown('<h1 class="main-header">🇻🇳 Vietnam Stock Analysis System - DEMO</h1>', unsafe_allow_html=True)
        st.markdown("### Deep insights with smart money tracking and EIC analysis")

        # Demo badge
        st.info("🧪 **DEMO MODE** - This is a demonstration of the web interface with sample analysis data from BID and VCB banking analysis.")

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
                    ['BID', 'VCB'] + [s for s in self.popular_stocks if s not in ['BID', 'VCB']],
                    help="Demo data available for BID and VCB"
                )
            else:
                selected_symbol = st.text_input(
                    "Enter stock symbol:",
                    value="BID",
                    help="Demo data available for BID and VCB"
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

        # Demo data notice
        st.markdown("---")
        st.subheader("🧪 Demo Data Available")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            #### 🏦 BID - Bank for Investment and Development
            - **Composite Score**: 54.6/100 (B - Hold)
            - **EIC Score**: 65.4/100 (EIC-B+)
            - **Smart Money**: Moderate Inflow
            - **Trend**: Bullish across timeframes
            """)

        with col2:
            st.markdown("""
            #### 🏦 VCB - Vietcombank
            - **Composite Score**: 78.3/100 (A - Buy)
            - **EIC Score**: 75.8/100 (EIC-A)
            - **Smart Money**: Strong Inflow
            - **Trend**: Strong Bullish momentum
            """)

        st.info("💡 **Try the demo**: Select BID or VCB from the sidebar and click 'Analyze Stock' to see the full analysis interface!")

    def get_demo_data(self, symbol):
        """Get demo data for a symbol"""
        if symbol in DEMO_ANALYSIS:
            return DEMO_ANALYSIS[symbol]
        else:
            # Return placeholder data for other symbols
            return {
                'comprehensive_analysis': {
                    'composite_score': 50.0,
                    'investment_grade': 'Demo - No Data',
                    'recommended_action': 'Demo Mode - Limited Data Available',
                    'time_horizon': 'Demo',
                    'confidence_level': 'Demo'
                },
                'eic_analysis': {
                    'eic_score': 50.0,
                    'eic_grade': 'Demo Mode',
                    'environment_score': 50.0,
                    'infrastructure_score': 50.0,
                    'competitiveness_score': 50.0
                },
                'technical_analysis': {
                    'current_price': 0,
                    'week_52_high': 0,
                    'week_52_low': 0,
                    'position_in_range': 50,
                    'annual_return': 0,
                    'volatility': 0,
                    'trend': 'Demo',
                    'support': 0,
                    'resistance': 0
                },
                'smart_money': {
                    'flow_direction': 'Demo Mode',
                    'confidence': 'Demo',
                    'signals': ['Demo data - Full analysis available for BID and VCB']
                }
            }

    def show_comprehensive_analysis(self, symbol: str):
        """Show comprehensive analysis dashboard"""

        st.subheader(f"📊 Comprehensive Analysis: {symbol}")

        # Get demo data
        data = self.get_demo_data(symbol)

        if symbol not in DEMO_ANALYSIS:
            st.warning(f"⚠️ Demo data not available for {symbol}. Full analysis available for BID and VCB.")
            st.info("In the production system, this would show real-time analysis for any Vietnamese stock.")

        # Display key metrics
        comp_analysis = data['comprehensive_analysis']
        eic_analysis = data['eic_analysis']
        technical = data['technical_analysis']

        # Key metrics row
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Composite Score",
                f"{comp_analysis['composite_score']:.1f}/100",
                delta=f"{comp_analysis['composite_score'] - 50:.1f}" if comp_analysis['composite_score'] != 50 else None
            )

        with col2:
            st.metric("Smart Money Flow", data['smart_money']['flow_direction'])

        with col3:
            st.metric(
                "EIC Score",
                f"{eic_analysis['eic_score']:.1f}/100",
                delta=f"{eic_analysis['eic_score'] - 50:.1f}" if eic_analysis['eic_score'] != 50 else None
            )

        with col4:
            st.metric("Technical Trend", technical['trend'])

        # Investment recommendation
        st.markdown("---")
        recommendation = comp_analysis['recommended_action']

        if 'Buy' in recommendation and 'Strong' not in recommendation:
            st.markdown(f'<div class="signal-buy">📈 {recommendation}</div>', unsafe_allow_html=True)
        elif 'Hold' in recommendation:
            st.markdown(f'<div class="signal-hold">📊 {recommendation}</div>', unsafe_allow_html=True)
        else:
            st.info(f"📊 {recommendation}")

        # Detailed analysis tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Executive Summary",
            "🔍 Technical Analysis",
            "🏢 EIC Analysis",
            "🧠 Smart Money",
            "📊 Key Metrics"
        ])

        with tab1:
            st.markdown("### 🎯 Investment Thesis")
            st.markdown(f"**{symbol}** presents a **{comp_analysis['investment_grade'].lower()}** opportunity with a composite score of **{comp_analysis['composite_score']:.1f}/100**.")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### ✅ Key Strengths")
                if symbol == 'BID':
                    strengths = [
                        "State-owned bank with government backing",
                        "Strong competitive position (72.6/100)",
                        "Bullish technical trend across timeframes",
                        "Trading near 52-week highs"
                    ]
                elif symbol == 'VCB':
                    strengths = [
                        "Leading Vietnamese commercial bank",
                        "Excellent EIC profile (75.8/100)",
                        "Strong smart money inflow detected",
                        "Consistent outperformance"
                    ]
                else:
                    strengths = ["Demo mode - Limited analysis available"]

                for strength in strengths:
                    st.markdown(f"• {strength}")

            with col2:
                st.markdown("#### ⚠️ Risk Factors")
                if symbol == 'BID':
                    risks = [
                        "Moderate overall score suggests caution",
                        "24% volatility indicates price swings",
                        "Banking sector regulatory risks"
                    ]
                elif symbol == 'VCB':
                    risks = [
                        "Premium valuation near highs",
                        "Interest rate sensitivity",
                        "Market concentration risk"
                    ]
                else:
                    risks = ["Demo mode - Limited risk analysis"]

                for risk in risks:
                    st.markdown(f"• {risk}")

        with tab2:
            st.markdown("### 📈 Technical Analysis")

            if symbol in DEMO_ANALYSIS:
                # Price metrics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Current Price", f"{technical['current_price']:,} VND")
                with col2:
                    st.metric("52W High", f"{technical['week_52_high']:,} VND")
                with col3:
                    st.metric("52W Low", f"{technical['week_52_low']:,} VND")

                # Position in range
                st.markdown(f"**Position in 52W Range**: {technical['position_in_range']:.1f}%")
                progress_color = "green" if technical['position_in_range'] > 70 else "orange" if technical['position_in_range'] > 30 else "red"
                st.progress(technical['position_in_range']/100)

                # Performance metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Annual Return", f"{technical['annual_return']:.1f}%")
                with col2:
                    st.metric("Volatility", f"{technical['volatility']:.1f}%")
                with col3:
                    st.metric("Support", f"{technical['support']:,.0f} VND")
                with col4:
                    st.metric("Resistance", f"{technical['resistance']:,.0f} VND")

                # Technical chart simulation
                st.markdown("#### 📊 Price Chart Simulation")

                # Create mock price data
                dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
                np.random.seed(42 if symbol == 'BID' else 123)

                if symbol == 'BID':
                    base_price = 35
                    trend = 0.02
                else:
                    base_price = 70
                    trend = 0.03

                prices = []
                current_price = base_price

                for i, date in enumerate(dates):
                    daily_change = np.random.normal(trend/252, 0.02)
                    current_price *= (1 + daily_change)
                    prices.append(current_price)

                chart_data = pd.DataFrame({
                    'Date': dates,
                    'Price': prices
                })

                fig = px.line(chart_data, x='Date', y='Price', title=f'{symbol} Price Trend (Simulated)')
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)

            else:
                st.info("Technical analysis available in full system for all Vietnamese stocks")

        with tab3:
            st.markdown("### 🏢 EIC Framework Analysis")

            # EIC component scores
            categories = ['Environment', 'Infrastructure', 'Competitiveness']
            values = [
                eic_analysis['environment_score'],
                eic_analysis['infrastructure_score'],
                eic_analysis['competitiveness_score']
            ]

            # Create radar chart
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=f'{symbol} EIC Scores',
                fillcolor='rgba(30, 61, 89, 0.3)',
                line=dict(color='rgb(30, 61, 89)')
            ))

            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )),
                showlegend=True,
                title=f"{symbol} EIC Component Analysis",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # EIC breakdown
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("🌍 Environment", f"{eic_analysis['environment_score']:.1f}/100")
                st.caption("Market conditions & sector trends")

            with col2:
                st.metric("🏗️ Infrastructure", f"{eic_analysis['infrastructure_score']:.1f}/100")
                st.caption("Business fundamentals & operations")

            with col3:
                st.metric("🏆 Competitiveness", f"{eic_analysis['competitiveness_score']:.1f}/100")
                st.caption("Market position & advantages")

        with tab4:
            st.markdown("### 🧠 Smart Money Analysis")

            smart_money = data['smart_money']

            col1, col2, col3 = st.columns(3)

            with col1:
                flow_direction = smart_money['flow_direction']
                if 'Strong Inflow' in flow_direction:
                    st.success(f"📈 {flow_direction}")
                elif 'Inflow' in flow_direction:
                    st.info(f"📊 {flow_direction}")
                else:
                    st.warning(f"⚠️ {flow_direction}")

            with col2:
                st.metric("Confidence Level", smart_money['confidence'])

            with col3:
                signal_count = len(smart_money['signals'])
                st.metric("Active Signals", signal_count)

            st.markdown("#### 🎯 Smart Money Signals")
            for i, signal in enumerate(smart_money['signals'], 1):
                st.markdown(f"**{i}.** {signal}")

            if symbol in DEMO_ANALYSIS:
                # Mock volume analysis chart
                st.markdown("#### 📊 Volume Flow Analysis")

                # Create mock volume data
                dates = pd.date_range(start='2024-11-01', end='2024-12-15', freq='D')
                np.random.seed(42 if symbol == 'BID' else 123)

                volumes = []
                base_volume = 2000000 if symbol == 'BID' else 1500000

                for date in dates:
                    daily_volume = base_volume * (1 + np.random.normal(0, 0.3))
                    volumes.append(max(daily_volume, base_volume * 0.3))

                volume_data = pd.DataFrame({
                    'Date': dates,
                    'Volume': volumes
                })

                fig = px.bar(volume_data, x='Date', y='Volume', title=f'{symbol} Trading Volume (Simulated)')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

        with tab5:
            st.markdown("### 📊 Key Performance Metrics")

            if symbol in DEMO_ANALYSIS:
                # Create metrics summary
                metrics_data = {
                    'Metric': [
                        'Composite Investment Score',
                        'EIC Framework Score',
                        'Technical Trend Strength',
                        'Smart Money Confidence',
                        'Risk Level',
                        'Time Horizon',
                        'Position in 52W Range',
                        'Annual Return'
                    ],
                    'Value': [
                        f"{comp_analysis['composite_score']:.1f}/100",
                        f"{eic_analysis['eic_score']:.1f}/100",
                        technical['trend'],
                        smart_money['confidence'],
                        'Medium',
                        comp_analysis['time_horizon'],
                        f"{technical['position_in_range']:.1f}%",
                        f"{technical['annual_return']:.1f}%"
                    ],
                    'Status': [
                        '🟡' if comp_analysis['composite_score'] < 60 else '🟢',
                        '🟡' if eic_analysis['eic_score'] < 70 else '🟢',
                        '🟢' if 'Bullish' in technical['trend'] else '🟡',
                        '🟡' if smart_money['confidence'] == 'Medium' else '🟢',
                        '🟡',
                        '🟢',
                        '🟢' if technical['position_in_range'] > 70 else '🟡',
                        '🟢' if technical['annual_return'] > 5 else '🟡'
                    ]
                }

                df = pd.DataFrame(metrics_data)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Detailed metrics available for all stocks in production system")

    def show_smart_money_signals(self, symbol: str):
        """Show smart money signals dashboard"""

        st.subheader(f"🎯 Smart Money Signals: {symbol}")

        data = self.get_demo_data(symbol)

        if symbol not in DEMO_ANALYSIS:
            st.warning(f"⚠️ Demo data not available for {symbol}. Try BID or VCB for full demo experience.")

        smart_money = data['smart_money']

        # Signal overview
        col1, col2, col3 = st.columns(3)

        with col1:
            if symbol == 'BID':
                score = 67.5
            elif symbol == 'VCB':
                score = 84.2
            else:
                score = 50.0
            st.metric("Smart Money Score", f"{score:.1f}/100")

        with col2:
            flow = smart_money['flow_direction']
            if 'Strong' in flow:
                st.success(flow)
            elif 'Moderate' in flow:
                st.info(flow)
            else:
                st.warning(flow)

        with col3:
            st.metric("Signal Confidence", smart_money['confidence'])

        # Signal components
        st.markdown("### 🔍 Signal Components")

        if symbol in DEMO_ANALYSIS:
            # Mock signal components
            if symbol == 'BID':
                components = {
                    'Volume Analysis': 68,
                    'Price Action': 72,
                    'Accumulation Pattern': 65,
                    'Institutional Flow': 66
                }
            else:  # VCB
                components = {
                    'Volume Analysis': 86,
                    'Price Action': 82,
                    'Accumulation Pattern': 88,
                    'Institutional Flow': 81
                }

            # Create bar chart
            fig = px.bar(
                x=list(components.values()),
                y=list(components.keys()),
                orientation='h',
                title='Signal Component Breakdown',
                color=list(components.values()),
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)

        # Action recommendations
        st.markdown("### 💡 Actionable Recommendations")

        if symbol == 'BID':
            recommendations = [
                "Monitor for entry opportunities on minor pullbacks",
                "Set stop loss at 37.55 VND (support level)",
                "Target resistance at 45.1 VND for profit taking",
                "Position size: 2-3% of portfolio (moderate conviction)"
            ]
        elif symbol == 'VCB':
            recommendations = [
                "Strong accumulation signals - consider building position",
                "Entry on any weakness below 85 VND",
                "Multiple target levels: 95 VND, 100 VND, 105 VND",
                "Position size: 3-5% of portfolio (high conviction)"
            ]
        else:
            recommendations = ["Demo mode - Full recommendations available for BID and VCB"]

        for i, rec in enumerate(recommendations, 1):
            st.markdown(f"**{i}.** {rec}")

    def show_eic_analysis(self, symbol: str):
        """Show EIC framework analysis"""

        st.subheader(f"🏢 EIC Framework Analysis: {symbol}")

        data = self.get_demo_data(symbol)
        eic = data['eic_analysis']

        # Main EIC score
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("EIC Score", f"{eic['eic_score']:.1f}/100")
        with col2:
            st.metric("EIC Grade", eic['eic_grade'])
        with col3:
            st.metric("Sector", "Banks")

        if symbol in DEMO_ANALYSIS:
            # Component breakdown
            st.markdown("### 📊 EIC Component Analysis")

            components = ['Environment', 'Infrastructure', 'Competitiveness']
            scores = [eic['environment_score'], eic['infrastructure_score'], eic['competitiveness_score']]

            # Radar chart
            fig = go.Figure()

            fig.add_trace(go.Scatterpolar(
                r=scores,
                theta=components,
                fill='toself',
                name=f'{symbol} EIC Profile',
                fillcolor='rgba(30, 61, 89, 0.2)',
                line=dict(color='rgb(30, 61, 89)')
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
                showlegend=True,
                title=f"{symbol} EIC Analysis",
                height=500
            )

            st.plotly_chart(fig, use_container_width=True)

            # Component details
            env_tab, infra_tab, comp_tab = st.tabs(["🌍 Environment", "🏗️ Infrastructure", "🏆 Competitiveness"])

            with env_tab:
                st.metric("Environment Score", f"{eic['environment_score']:.1f}/100")

                if symbol == 'BID':
                    st.markdown("""
                    **Market Environment Analysis:**
                    - Banking sector showing stable conditions
                    - Government policy support for state banks
                    - Interest rate environment moderately favorable
                    - Credit growth targets supportive
                    """)
                elif symbol == 'VCB':
                    st.markdown("""
                    **Market Environment Analysis:**
                    - Strong banking sector fundamentals
                    - Leading market position benefits
                    - Favorable regulatory environment
                    - Digital banking trends supportive
                    """)

            with infra_tab:
                st.metric("Infrastructure Score", f"{eic['infrastructure_score']:.1f}/100")

                if symbol == 'BID':
                    st.markdown("""
                    **Infrastructure Assessment:**
                    - Extensive branch network nationwide
                    - Government backing provides stability
                    - Capital adequacy meets requirements
                    - Digital transformation in progress
                    """)
                elif symbol == 'VCB':
                    st.markdown("""
                    **Infrastructure Assessment:**
                    - Modern banking infrastructure
                    - Strong digital platform capabilities
                    - Excellent capital adequacy ratios
                    - Efficient operational structure
                    """)

            with comp_tab:
                st.metric("Competitiveness Score", f"{eic['competitiveness_score']:.1f}/100")

                if symbol == 'BID':
                    st.markdown("""
                    **Competitive Position:**
                    - Strong market share in corporate banking
                    - State ownership provides competitive edge
                    - Established customer relationships
                    - Pricing power in key segments
                    """)
                elif symbol == 'VCB':
                    st.markdown("""
                    **Competitive Position:**
                    - Market leader in Vietnamese banking
                    - Superior brand recognition and trust
                    - Innovation in digital services
                    - Strong competitive moats
                    """)
        else:
            st.info("Detailed EIC analysis available for all stocks in production system")

    def show_market_maker_analysis(self, symbol: str):
        """Show market maker analysis"""

        st.subheader(f"💹 Market Maker Analysis: {symbol}")

        if symbol not in DEMO_ANALYSIS:
            st.warning(f"⚠️ Demo data not available for {symbol}. Try BID or VCB.")

        # Mock market maker data
        if symbol == 'BID':
            mm_data = {
                'style': 'Professional Market Maker',
                'aggression': 'Conservative',
                'efficiency': 72.3,
                'phase': 'Consolidation',
                'liquidity_grade': 'B - Good'
            }
        elif symbol == 'VCB':
            mm_data = {
                'style': 'Active Liquidity Provider',
                'aggression': 'Moderate',
                'efficiency': 84.1,
                'phase': 'Accumulation',
                'liquidity_grade': 'A - Excellent'
            }
        else:
            mm_data = {
                'style': 'Demo Mode',
                'aggression': 'Demo',
                'efficiency': 50,
                'phase': 'Demo',
                'liquidity_grade': 'Demo'
            }

        # Market maker profile
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("MM Style", mm_data['style'])
        with col2:
            st.metric("Aggression Level", mm_data['aggression'])
        with col3:
            st.metric("Efficiency Score", f"{mm_data['efficiency']:.1f}/100")

        st.markdown("### 📊 Market Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.info(f"**Current Phase**: {mm_data['phase']}")

        with col2:
            st.info(f"**Liquidity Grade**: {mm_data['liquidity_grade']}")

        if symbol in DEMO_ANALYSIS:
            st.markdown("### 💡 Market Maker Insights")

            if symbol == 'BID':
                insights = [
                    "Professional market making with tight spreads",
                    "Conservative approach indicates stability focus",
                    "Consolidation phase suggests accumulation opportunity",
                    "Good liquidity provision for institutional size"
                ]
            elif symbol == 'VCB':
                insights = [
                    "Active liquidity provider with strong efficiency",
                    "Accumulation phase indicates building momentum",
                    "Excellent liquidity supports large position sizes",
                    "Moderate aggression suggests controlled upside"
                ]
            else:
                insights = ["Demo mode insights"]

            for insight in insights:
                st.markdown(f"• {insight}")

    def show_stock_universe(self):
        """Show stock universe overview"""

        st.subheader("🌏 Vietnam Stock Universe")

        # Sample sector data
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

        # Pie chart
        fig = px.pie(
            values=list(sector_data.values()),
            names=list(sector_data.keys()),
            title="Stock Distribution by Sector"
        )
        st.plotly_chart(fig, use_container_width=True)

        # Top stocks table
        st.markdown("### 🚀 Sample Top Liquid Stocks")

        sample_data = [
            {'Symbol': 'VCB', 'Sector': 'Banks', 'Liquidity Score': 95.2, 'Demo Status': '✅ Available'},
            {'Symbol': 'BID', 'Sector': 'Banks', 'Liquidity Score': 87.3, 'Demo Status': '✅ Available'},
            {'Symbol': 'VIC', 'Sector': 'Real Estate', 'Liquidity Score': 92.8, 'Demo Status': '🔄 Production'},
            {'Symbol': 'FPT', 'Sector': 'Technology', 'Liquidity Score': 89.5, 'Demo Status': '🔄 Production'},
            {'Symbol': 'HPG', 'Sector': 'Steel', 'Liquidity Score': 85.9, 'Demo Status': '🔄 Production'}
        ]

        df = pd.DataFrame(sample_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.info("💡 **Production System**: Covers 500+ liquid Vietnamese stocks with real-time analysis")

    def show_multi_stock_comparison(self):
        """Show multi-stock comparison"""

        st.subheader("📈 Multi-Stock Comparison")

        st.info("🧪 **Demo Mode**: Comparison feature available with sample data")

        # Sample comparison
        comparison_data = [
            {
                'Symbol': 'VCB',
                'Composite Score': 78.3,
                'EIC Score': 75.8,
                'Smart Money': 'Strong Inflow',
                'Recommendation': 'Buy'
            },
            {
                'Symbol': 'BID',
                'Composite Score': 54.6,
                'EIC Score': 65.4,
                'Smart Money': 'Moderate Inflow',
                'Recommendation': 'Hold'
            }
        ]

        df = pd.DataFrame(comparison_data)
        df = df.sort_values('Composite Score', ascending=False)

        st.dataframe(df, use_container_width=True, hide_index=True)

        # Comparison chart
        fig = px.bar(
            df,
            x='Symbol',
            y='Composite Score',
            title='Banking Stocks Comparison',
            color='Composite Score',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main function to run the demo app"""
    demo_app = VietnamStockAnalysisDemo()
    demo_app.run()

if __name__ == "__main__":
    main()