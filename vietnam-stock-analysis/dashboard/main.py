#!/usr/bin/env python3
"""
Vietnam Stock Analysis Dashboard
Comprehensive trading dashboard with technical analysis and portfolio tracking
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from shared.models.database import get_db
from shared.analysis.smart_money import SmartMoneyAnalyzer

# Configure page
st.set_page_config(
    page_title="Vietnam Stock Analysis",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .positive { color: #00C851; }
    .negative { color: #ff4444; }
    .neutral { color: #33b5e5; }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_stock_data():
    """Load all stock data from database"""
    db = get_db()
    stocks = db.get_all_stocks()
    return pd.DataFrame(stocks)

@st.cache_data(ttl=300)
def load_price_data(symbol, days_back=30):
    """Load price data for a specific symbol"""
    db = get_db()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')

    price_data = db.get_price_data(symbol, start_date, end_date)
    if not price_data:
        return pd.DataFrame()

    df = pd.DataFrame(price_data)
    df['date'] = pd.to_datetime(df['date'])
    return df.sort_values('date')

def calculate_technical_indicators(df):
    """Calculate technical analysis indicators"""
    if df.empty or len(df) < 20:
        return df

    # Moving averages
    df['ma_5'] = df['close'].rolling(window=5).mean()
    df['ma_10'] = df['close'].rolling(window=10).mean()
    df['ma_20'] = df['close'].rolling(window=20).mean()

    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    exp1 = df['close'].ewm(span=12).mean()
    exp2 = df['close'].ewm(span=26).mean()
    df['macd'] = exp1 - exp2
    df['macd_signal'] = df['macd'].ewm(span=9).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']

    # Bollinger Bands
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    bb_std = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (bb_std * 2)
    df['bb_lower'] = df['bb_middle'] - (bb_std * 2)

    return df

def create_candlestick_chart(df, symbol):
    """Create candlestick chart with technical indicators"""
    if df.empty:
        st.warning(f"No price data available for {symbol}")
        return

    # Create subplots
    fig = make_subplots(
        rows=4, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=('Price & Volume', 'RSI', 'MACD', 'Volume'),
        row_width=[0.2, 0.2, 0.2, 0.4]
    )

    # Candlestick chart
    fig.add_trace(
        go.Candlestick(
            x=df['date'],
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name=symbol
        ),
        row=1, col=1
    )

    # Moving averages
    if 'ma_5' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['ma_5'], name='MA5', line=dict(color='orange', width=1)),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['ma_20'], name='MA20', line=dict(color='blue', width=1)),
            row=1, col=1
        )

    # Bollinger Bands
    if 'bb_upper' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['bb_upper'], name='BB Upper',
                      line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['bb_lower'], name='BB Lower',
                      line=dict(color='gray', width=1, dash='dash')),
            row=1, col=1
        )

    # RSI
    if 'rsi' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['rsi'], name='RSI', line=dict(color='purple')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)

    # MACD
    if 'macd' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['macd'], name='MACD', line=dict(color='blue')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['date'], y=df['macd_signal'], name='Signal', line=dict(color='red')),
            row=3, col=1
        )
        fig.add_trace(
            go.Bar(x=df['date'], y=df['macd_histogram'], name='Histogram'),
            row=3, col=1
        )

    # Volume
    fig.add_trace(
        go.Bar(x=df['date'], y=df['volume'], name='Volume', marker_color='lightblue'),
        row=4, col=1
    )

    # Update layout
    fig.update_layout(
        title=f"{symbol} - Technical Analysis",
        xaxis_rangeslider_visible=False,
        height=800,
        showlegend=True
    )

    return fig

def display_stock_metrics(df, symbol):
    """Display key stock metrics"""
    if df.empty:
        return

    latest = df.iloc[-1]
    previous = df.iloc[-2] if len(df) > 1 else latest

    # Calculate metrics
    price_change = latest['close'] - previous['close']
    price_change_pct = (price_change / previous['close']) * 100

    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Current Price",
            value=f"{latest['close']:,.0f} VND",
            delta=f"{price_change:+.1f} ({price_change_pct:+.2f}%)"
        )

    with col2:
        high_52w = df['high'].max()
        low_52w = df['low'].min()
        st.metric(
            label="52W High",
            value=f"{high_52w:,.0f} VND"
        )
        st.metric(
            label="52W Low",
            value=f"{low_52w:,.0f} VND"
        )

    with col3:
        avg_volume = df['volume'].mean()
        st.metric(
            label="Avg Volume",
            value=f"{avg_volume:,.0f}"
        )
        st.metric(
            label="Latest Volume",
            value=f"{latest['volume']:,.0f}"
        )

    with col4:
        if 'rsi' in df.columns and not pd.isna(latest['rsi']):
            rsi_color = "🔴" if latest['rsi'] > 70 else "🟢" if latest['rsi'] < 30 else "🟡"
            st.metric(
                label="RSI (14)",
                value=f"{latest['rsi']:.1f} {rsi_color}"
            )

def main():
    """Main dashboard function"""
    st.title("📈 Vietnam Stock Analysis Dashboard")
    st.markdown("Real-time analysis of Vietnamese stock market data")

    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.selectbox(
        "Choose Analysis Type",
        ["Market Overview", "Stock Analysis", "Smart Signals", "Portfolio Tracker", "Economic Indicators"]
    )

    if page == "Market Overview":
        st.header("🏢 Market Overview")

        # Load stock data
        stocks_df = load_stock_data()

        if stocks_df.empty:
            st.warning("No stock data available. Please run data collection first.")
            return

        # Display stock list
        st.subheader("Available Stocks")

        # Add performance metrics
        for _, stock in stocks_df.iterrows():
            with st.expander(f"{stock['symbol']} - {stock['name']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Sector:** {stock['sector']}")
                    st.write(f"**Exchange:** {stock['exchange']}")
                with col2:
                    if stock['market_cap']:
                        st.write(f"**Market Cap:** {stock['market_cap']:,.0f} VND")

                # Load recent price data
                price_df = load_price_data(stock['symbol'], days_back=7)
                if not price_df.empty:
                    latest = price_df.iloc[-1]
                    previous = price_df.iloc[-2] if len(price_df) > 1 else latest
                    change = latest['close'] - previous['close']
                    change_pct = (change / previous['close']) * 100

                    color = "🟢" if change >= 0 else "🔴"
                    st.write(f"**Latest Price:** {latest['close']:,.0f} VND {color} ({change_pct:+.2f}%)")

    elif page == "Stock Analysis":
        st.header("📊 Individual Stock Analysis")

        # Stock selection
        stocks_df = load_stock_data()
        if stocks_df.empty:
            st.warning("No stock data available.")
            return

        symbols = stocks_df['symbol'].tolist()
        selected_symbol = st.selectbox("Select Stock Symbol", symbols)

        # Time period selection
        col1, col2 = st.columns(2)
        with col1:
            days_back = st.selectbox("Time Period", [7, 30, 90, 180, 365], index=1)
        with col2:
            show_indicators = st.checkbox("Show Technical Indicators", value=True)

        if selected_symbol:
            # Load and process data
            df = load_price_data(selected_symbol, days_back)

            if df.empty:
                st.warning(f"No price data available for {selected_symbol}")
                return

            # Calculate technical indicators if requested
            if show_indicators:
                df = calculate_technical_indicators(df)

            # Display metrics
            display_stock_metrics(df, selected_symbol)

            # Create and display chart
            fig = create_candlestick_chart(df, selected_symbol)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

            # Recent price movements table
            st.subheader("Recent Price Movements")
            recent_df = df[['date', 'open', 'high', 'low', 'close', 'volume']].tail(10)
            recent_df['change'] = recent_df['close'].diff()
            recent_df['change_pct'] = (recent_df['change'] / recent_df['close'].shift(1)) * 100

            st.dataframe(
                recent_df.style.format({
                    'open': '{:,.0f}',
                    'high': '{:,.0f}',
                    'low': '{:,.0f}',
                    'close': '{:,.0f}',
                    'volume': '{:,.0f}',
                    'change': '{:+.1f}',
                    'change_pct': '{:+.2f}%'
                }),
                use_container_width=True
            )

    elif page == "Smart Signals":
        st.header("🧠 Smart Money Signals")
        st.markdown("Advanced institutional behavior analysis for Vietnamese stocks")

        # Initialize Smart Money Analyzer
        @st.cache_resource
        def load_smart_analyzer():
            return SmartMoneyAnalyzer()

        analyzer = load_smart_analyzer()

        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["Market Overview", "Individual Analysis", "Sector Comparison", "Signal History"])

        with tab1:
            st.subheader("📊 Smart Money Market Overview")

            # Sector filtering for market overview
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown("**Sector Filter:**")
            with col2:
                sector_filter = st.selectbox(
                    "Select Sector",
                    ["All Sectors", "Banking", "Real Estate", "Steel", "Securities"],
                    key="market_sector_filter"
                )

            # Get market overview with sector filtering
            with st.spinner("Analyzing market-wide smart money signals..."):
                if sector_filter == "All Sectors":
                    market_overview = analyzer.get_market_overview()
                else:
                    # Filter by sector
                    market_overview = analyzer.get_market_overview(sector_filter=sector_filter.lower().replace(" ", "_"))

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Market Sentiment",
                    market_overview['market_sentiment'],
                    help="Overall smart money sentiment across analyzed stocks"
                )

            with col2:
                st.metric(
                    "Strong Signals",
                    len(market_overview['strong_signals']),
                    help="Stocks with bullish smart money signals"
                )

            with col3:
                st.metric(
                    "Weak Signals",
                    len(market_overview['weak_signals']),
                    help="Stocks with bearish smart money signals"
                )

            # Top Picks
            if market_overview['top_picks']:
                st.subheader("🎯 Top Smart Money Picks")

                for pick in market_overview['top_picks']:
                    with st.expander(f"🔥 {pick['symbol']} - {pick['name']} (Score: {pick['score']:.1f})"):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Signal:** {pick['signal']}")
                            st.write(f"**Score:** {pick['score']:.1f}/100")
                        with col2:
                            if st.button(f"Analyze {pick['symbol']}", key=f"analyze_{pick['symbol']}"):
                                st.session_state.selected_symbol = pick['symbol']
                                st.session_state.switch_to_individual = True

            # Strong Signals Table
            if market_overview['strong_signals']:
                st.subheader("📈 Bullish Signals")
                strong_df = pd.DataFrame(market_overview['strong_signals'])
                st.dataframe(
                    strong_df.style.format({'score': '{:.1f}'}),
                    use_container_width=True
                )

            # Weak Signals Table
            if market_overview['weak_signals']:
                st.subheader("📉 Bearish Signals")
                weak_df = pd.DataFrame(market_overview['weak_signals'])
                st.dataframe(
                    weak_df.style.format({'score': '{:.1f}'}),
                    use_container_width=True
                )

        with tab2:
            st.subheader("🔍 Individual Stock Analysis")

            # Stock selection with sector filtering
            stocks_df = load_stock_data()
            if stocks_df.empty:
                st.warning("No stock data available.")
            else:
                # Sector and stock selection
                col1, col2 = st.columns(2)

                with col1:
                    individual_sector_filter = st.selectbox(
                        "Filter by Sector",
                        ["All Sectors", "Banking", "Real Estate", "Steel", "Securities"],
                        key="individual_sector_filter"
                    )

                # Filter stocks by sector
                if individual_sector_filter != "All Sectors":
                    sector_name = individual_sector_filter.lower().replace(" ", "_")
                    filtered_stocks = stocks_df[stocks_df['sector'] == sector_name]
                    if filtered_stocks.empty:
                        st.warning(f"No stocks available for {individual_sector_filter} sector.")
                        symbols = []
                    else:
                        symbols = filtered_stocks['symbol'].tolist()
                else:
                    symbols = stocks_df['symbol'].tolist()

                if symbols:
                    with col2:
                        # Handle automatic selection from market overview
                        default_index = 0
                        if hasattr(st.session_state, 'selected_symbol') and st.session_state.selected_symbol in symbols:
                            default_index = symbols.index(st.session_state.selected_symbol)
                            delattr(st.session_state, 'selected_symbol')

                        selected_symbol = st.selectbox(
                            "Select Stock for Analysis",
                            symbols,
                            index=default_index,
                            key="stock_selector"
                        )

                col1, col2 = st.columns(2)
                with col1:
                    analysis_period = st.selectbox("Analysis Period", [30, 60, 90], index=1)
                with col2:
                    if st.button("🔄 Refresh Analysis", type="primary"):
                        st.cache_data.clear()

                if selected_symbol:
                    with st.spinner(f"Analyzing smart money signals for {selected_symbol}..."):
                        analysis = analyzer.analyze_symbol(selected_symbol, days_back=analysis_period)

                    if 'error' in analysis:
                        st.error(f"Analysis error: {analysis['error']}")
                    else:
                        # Main metrics
                        st.subheader("📊 Signal Summary")
                        composite = analysis['composite_score']

                        col1, col2, col3, col4 = st.columns(4)

                        with col1:
                            score_color = "🟢" if composite['composite_score'] >= 60 else "🔴" if composite['composite_score'] <= 40 else "🟡"
                            st.metric(
                                "Composite Score",
                                f"{composite['composite_score']:.1f} {score_color}",
                                help="Overall smart money signal strength (0-100)"
                            )

                        with col2:
                            st.metric(
                                "Signal Class",
                                composite['signal_class'],
                                help="Trading recommendation based on signals"
                            )

                        with col3:
                            st.metric(
                                "Signal Strength",
                                composite['signal_strength'],
                                help="Confidence level of the signals"
                            )

                        with col4:
                            risk_grade = analysis['risk_analysis']['risk_grade']
                            st.metric(
                                "Risk Grade",
                                risk_grade,
                                help="Risk assessment for the position"
                            )

                        # Recommended Action
                        st.info(f"**Recommended Action:** {composite['recommended_action']}")

                        # Signal Components Breakdown
                        st.subheader("🔬 Signal Components")

                        components = composite['component_scores']
                        component_data = []
                        for component, score in components.items():
                            component_data.append({
                                'Component': component.replace('_', ' ').title(),
                                'Score': score,
                                'Status': '🟢 Strong' if score >= 65 else '🔴 Weak' if score <= 35 else '🟡 Neutral'
                            })

                        component_df = pd.DataFrame(component_data)
                        st.dataframe(component_df, use_container_width=True)

                        # Signal Components Chart
                        fig_components = px.bar(
                            component_df,
                            x='Component',
                            y='Score',
                            title="Signal Component Breakdown",
                            color='Score',
                            color_continuous_scale='RdYlGn'
                        )
                        fig_components.add_hline(y=50, line_dash="dash", line_color="gray",
                                               annotation_text="Neutral (50)")
                        st.plotly_chart(fig_components, use_container_width=True)

                        # Detailed Signal Analysis
                        col1, col2 = st.columns(2)

                        with col1:
                            st.subheader("📈 Entry/Exit Signals")
                            entry_exit = analysis['entry_exit_signals']

                            if entry_exit['entry_signals']:
                                st.write("**Entry Signals:**")
                                for signal in entry_exit['entry_signals']:
                                    urgency_color = "🔥" if signal['urgency'] == 'High' else "🟡"
                                    st.write(f"• {urgency_color} **{signal['type']}** at {signal['level']:.0f} VND")
                            else:
                                st.write("⏳ No clear entry signals currently")

                            if entry_exit['stop_loss']:
                                st.write(f"**Stop Loss:** {entry_exit['stop_loss']:.0f} VND")

                            if entry_exit['targets']:
                                st.write("**Targets:**")
                                for i, target in enumerate(entry_exit['targets'], 1):
                                    st.write(f"• Target {i}: {target:.0f} VND")

                            st.write(f"**Position Sizing:** {entry_exit['position_sizing']}")

                        with col2:
                            st.subheader("⚠️ Risk Analysis")
                            risk = analysis['risk_analysis']

                            st.write(f"**Volatility:** {risk['volatility']:.1f}%")
                            st.write(f"**Max Drawdown:** {risk['max_drawdown']:.1f}%")
                            st.write(f"**VaR (95%):** {risk['var_95']:.2f}%")
                            st.write(f"**Liquidity Score:** {risk['liquidity_score']:.0f}/100")

                        # Market Context
                        st.subheader("🇻🇳 Vietnamese Market Context")
                        context = analysis['market_context']

                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Original Score:** {context['original_score']:.1f}")
                            st.write(f"**Adjusted Score:** {context['adjusted_score']:.1f}")
                            st.write(f"**Adjustment Factor:** {context['adjustment_factor']:.2f}x")

                        with col2:
                            if context['context_notes']:
                                st.write("**Market Factors:**")
                                for note in context['context_notes']:
                                    st.write(f"• {note}")

                        # Actionable Insights
                        st.subheader("💡 Actionable Insights")
                        insights = analysis['actionable_insights']

                        col1, col2 = st.columns(2)

                        with col1:
                            if insights['opportunities']:
                                st.write("**Opportunities:**")
                                for opp in insights['opportunities']:
                                    st.write(f"• 🎯 {opp}")

                            if insights['next_actions']:
                                st.write("**Next Actions:**")
                                for action in insights['next_actions']:
                                    st.write(f"• ⚡ {action}")

                        with col2:
                            if insights['risks']:
                                st.write("**Key Risks:**")
                                for risk in insights['risks']:
                                    st.write(f"• ⚠️ {risk}")

                            if insights['key_points']:
                                st.write("**Key Points:**")
                                for point in insights['key_points']:
                                    st.write(f"• 📌 {point}")

                        # Detailed Signal Information
                        with st.expander("🔍 Detailed Signal Analysis"):
                            signal_components = analysis['signal_components']

                            for component_name, component_data in signal_components.items():
                                st.write(f"**{component_name.replace('_', ' ').title()}**")

                                if 'signals' in component_data and component_data['signals']:
                                    for signal in component_data['signals']:
                                        signal_icon = "🟢" if signal.get('bullish', True) else "🔴"
                                        st.write(f"  {signal_icon} {signal['description']} ({signal['strength']})")
                                elif 'patterns' in component_data and component_data['patterns']:
                                    for pattern in component_data['patterns']:
                                        pattern_icon = "🟢" if pattern.get('bullish', True) else "🔴"
                                        st.write(f"  {pattern_icon} {pattern['description']}")

                                st.write("")

        with tab3:
            st.subheader("🏢 Sector Comparison")
            st.markdown("Compare smart money signals across Vietnamese market sectors")

            # Get sector analysis
            with st.spinner("Analyzing sector performance..."):
                db = get_db()
                all_stocks = db.get_all_stocks()

                # Group stocks by sector
                sectors = {}
                for stock in all_stocks:
                    sector = stock['sector']
                    if sector not in sectors:
                        sectors[sector] = []
                    sectors[sector].append(stock['symbol'])

                # Analyze each sector
                sector_results = {}
                for sector, symbols in sectors.items():
                    sector_scores = []
                    sector_signals = []

                    for symbol in symbols:
                        try:
                            analysis = analyzer.analyze_symbol(symbol, days_back=60)
                            if 'error' not in analysis:
                                score = analysis['market_context']['adjusted_score']
                                signal = analysis['composite_score']['signal_class']
                                sector_scores.append(score)
                                sector_signals.append(signal)
                        except:
                            continue

                    if sector_scores:
                        sector_results[sector] = {
                            'avg_score': sum(sector_scores) / len(sector_scores),
                            'max_score': max(sector_scores),
                            'min_score': min(sector_scores),
                            'stock_count': len(symbols),
                            'analyzed_count': len(sector_scores),
                            'signals': sector_signals,
                            'scores': sector_scores
                        }

            # Display sector comparison
            if sector_results:
                # Sector performance table
                st.subheader("📊 Sector Performance Summary")

                sector_data = []
                for sector, data in sector_results.items():
                    score_range = data['max_score'] - data['min_score']
                    signal_diversity = len(set(data['signals']))

                    sector_data.append({
                        'Sector': sector.replace('_', ' ').title(),
                        'Avg Score': f"{data['avg_score']:.1f}",
                        'Score Range': f"{score_range:.1f}",
                        'Stocks': f"{data['analyzed_count']}/{data['stock_count']}",
                        'Signal Types': signal_diversity,
                        'Top Signal': max(set(data['signals']), key=data['signals'].count) if data['signals'] else 'N/A'
                    })

                sector_df = pd.DataFrame(sector_data)
                st.dataframe(
                    sector_df.style.background_gradient(subset=['Avg Score'], cmap='RdYlGn'),
                    use_container_width=True
                )

                # Visual comparison
                st.subheader("📈 Sector Score Distribution")

                col1, col2 = st.columns(2)

                with col1:
                    # Average scores by sector
                    avg_scores = {sector.replace('_', ' ').title(): data['avg_score']
                                for sector, data in sector_results.items()}

                    sector_chart_data = pd.DataFrame(
                        list(avg_scores.items()),
                        columns=['Sector', 'Average Score']
                    )

                    st.bar_chart(sector_chart_data.set_index('Sector'))

                with col2:
                    # Score ranges by sector
                    range_data = {sector.replace('_', ' ').title(): data['max_score'] - data['min_score']
                                for sector, data in sector_results.items()}

                    range_chart_data = pd.DataFrame(
                        list(range_data.items()),
                        columns=['Sector', 'Score Range']
                    )

                    st.bar_chart(range_chart_data.set_index('Sector'))

                # Top performers by sector
                st.subheader("🏆 Top Performers by Sector")

                for sector, data in sector_results.items():
                    with st.expander(f"🏢 {sector.replace('_', ' ').title()} Sector ({data['analyzed_count']} stocks)"):
                        # Get detailed analysis for this sector
                        sector_symbols = sectors[sector]
                        sector_details = []

                        for symbol in sector_symbols:
                            try:
                                analysis = analyzer.analyze_symbol(symbol, days_back=60)
                                if 'error' not in analysis:
                                    sector_details.append({
                                        'Symbol': symbol,
                                        'Score': analysis['market_context']['adjusted_score'],
                                        'Signal': analysis['composite_score']['signal_class'],
                                        'Action': analysis['composite_score']['recommended_action']
                                    })
                            except:
                                continue

                        if sector_details:
                            sector_detail_df = pd.DataFrame(sector_details)
                            sector_detail_df = sector_detail_df.sort_values('Score', ascending=False)

                            st.dataframe(
                                sector_detail_df.style.format({'Score': '{:.1f}'}),
                                use_container_width=True
                            )

        with tab4:
            st.subheader("📜 Signal History")
            st.info("Signal history tracking coming soon! This will show historical performance of smart money signals.")

            # Placeholder for signal history
            st.write("**Features to be implemented:**")
            st.write("• Historical signal accuracy tracking")
            st.write("• Performance metrics over time")
            st.write("• Signal strength trends")
            st.write("• Backtesting results")

    elif page == "Portfolio Tracker":
        st.header("💼 Portfolio Tracker")

        # Get database instance
        db = get_db()

        # Portfolio overview
        portfolio_performance = db.get_portfolio_performance()

        if portfolio_performance['positions']:
            # Portfolio summary
            st.subheader("📊 Portfolio Summary")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Total Value",
                    f"{portfolio_performance['total_value']:,.0f} VND"
                )

            with col2:
                st.metric(
                    "Total Cost",
                    f"{portfolio_performance['total_cost']:,.0f} VND"
                )

            with col3:
                gain_loss = portfolio_performance['total_gain_loss']
                gain_loss_pct = portfolio_performance['total_gain_loss_pct']
                color = "🟢" if gain_loss >= 0 else "🔴"
                st.metric(
                    "Total P&L",
                    f"{gain_loss:,.0f} VND {color}",
                    f"{gain_loss_pct:+.2f}%"
                )

            with col4:
                num_positions = len(portfolio_performance['positions'])
                st.metric(
                    "Positions",
                    f"{num_positions}"
                )

            # Portfolio positions table
            st.subheader("📈 Current Positions")

            # Create DataFrame for portfolio display
            portfolio_df = pd.DataFrame(portfolio_performance['positions'])

            # Format and display
            display_df = portfolio_df[[
                'stock_symbol', 'name', 'position_size', 'entry_price',
                'current_price', 'gain_loss', 'gain_loss_pct'
            ]].copy()

            display_df.columns = [
                'Symbol', 'Name', 'Shares', 'Entry Price',
                'Current Price', 'P&L (VND)', 'P&L (%)'
            ]

            # Style the dataframe
            styled_df = display_df.style.format({
                'Entry Price': '{:,.0f}',
                'Current Price': '{:,.0f}',
                'P&L (VND)': '{:+,.0f}',
                'P&L (%)': '{:+.2f}%'
            }).applymap(
                lambda x: 'color: green' if x > 0 else 'color: red' if x < 0 else '',
                subset=['P&L (VND)', 'P&L (%)']
            )

            st.dataframe(styled_df, use_container_width=True)

            # Portfolio allocation pie chart
            st.subheader("🥧 Portfolio Allocation")
            allocation_data = []
            for position in portfolio_performance['positions']:
                allocation_data.append({
                    'Symbol': position['stock_symbol'],
                    'Value': position['position_value'],
                    'Percentage': (position['position_value'] / portfolio_performance['total_value']) * 100
                })

            allocation_df = pd.DataFrame(allocation_data)
            fig_pie = px.pie(
                allocation_df,
                values='Value',
                names='Symbol',
                title="Portfolio Allocation by Value"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        else:
            st.info("No positions in portfolio yet. Add your first position below!")

        # Add new position form
        st.subheader("➕ Add New Position")

        with st.form("add_position"):
            col1, col2, col3, col4 = st.columns(4)

            stocks_df = load_stock_data()
            available_symbols = stocks_df['symbol'].tolist() if not stocks_df.empty else []

            with col1:
                portfolio_symbol = st.selectbox("Stock Symbol", available_symbols)

            with col2:
                shares = st.number_input("Number of Shares", min_value=1, value=100)

            with col3:
                # Get current price as default
                if portfolio_symbol and not stocks_df.empty:
                    current_price_data = db.get_latest_price(portfolio_symbol)
                    default_price = current_price_data['close'] if current_price_data else 50000
                else:
                    default_price = 50000

                buy_price = st.number_input(
                    "Entry Price (VND)",
                    min_value=0.0,
                    value=float(default_price)
                )

            with col4:
                entry_date = st.date_input(
                    "Entry Date",
                    value=datetime.now().date()
                )

            submitted = st.form_submit_button("Add Position")

            if submitted and portfolio_symbol:
                success = db.add_portfolio_position(
                    stock_symbol=portfolio_symbol,
                    position_size=shares,
                    entry_price=buy_price,
                    entry_date=entry_date.strftime('%Y-%m-%d')
                )

                if success:
                    st.success(f"✅ Added {shares} shares of {portfolio_symbol} at {buy_price:,.0f} VND")
                    st.rerun()
                else:
                    st.error("❌ Failed to add position. Please try again.")

        # Position management
        if portfolio_performance['positions']:
            st.subheader("⚙️ Manage Positions")

            # Select position to manage
            position_options = []
            for pos in portfolio_performance['positions']:
                position_options.append(
                    f"{pos['stock_symbol']} - {pos['position_size']} shares @ {pos['entry_price']:,.0f} VND"
                )

            if position_options:
                selected_position_idx = st.selectbox(
                    "Select position to manage:",
                    range(len(position_options)),
                    format_func=lambda x: position_options[x]
                )

                selected_position = portfolio_performance['positions'][selected_position_idx]

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📊 View Details"):
                        st.json({
                            'Symbol': selected_position['stock_symbol'],
                            'Entry Date': selected_position['entry_date'],
                            'Current Value': f"{selected_position['position_value']:,.0f} VND",
                            'Unrealized P&L': f"{selected_position['gain_loss']:+,.0f} VND",
                            'Return %': f"{selected_position['gain_loss_pct']:+.2f}%"
                        })

                with col2:
                    if st.button("🗑️ Remove Position", type="secondary"):
                        if st.session_state.get('confirm_delete'):
                            success = db.remove_portfolio_position(selected_position['id'])
                            if success:
                                st.success("Position removed successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to remove position.")
                            st.session_state.confirm_delete = False
                        else:
                            st.session_state.confirm_delete = True
                            st.warning("Click again to confirm deletion")

        # Portfolio analytics
        if portfolio_performance['positions']:
            st.subheader("📈 Portfolio Analytics")

            # Performance by sector
            sector_performance = {}
            for position in portfolio_performance['positions']:
                sector = position['sector']
                if sector not in sector_performance:
                    sector_performance[sector] = {
                        'value': 0,
                        'cost': 0,
                        'positions': 0
                    }
                sector_performance[sector]['value'] += position['position_value']
                sector_performance[sector]['cost'] += position['position_cost']
                sector_performance[sector]['positions'] += 1

            # Create sector analysis
            sector_data = []
            for sector, data in sector_performance.items():
                gain_loss = data['value'] - data['cost']
                gain_loss_pct = (gain_loss / data['cost']) * 100 if data['cost'] > 0 else 0
                sector_data.append({
                    'Sector': sector,
                    'Value': data['value'],
                    'P&L': gain_loss,
                    'P&L %': gain_loss_pct,
                    'Positions': data['positions']
                })

            sector_df = pd.DataFrame(sector_data)

            col1, col2 = st.columns(2)

            with col1:
                st.write("**Performance by Sector**")
                st.dataframe(
                    sector_df.style.format({
                        'Value': '{:,.0f}',
                        'P&L': '{:+,.0f}',
                        'P&L %': '{:+.2f}%'
                    }),
                    use_container_width=True
                )

            with col2:
                # Sector allocation chart
                fig_sector = px.bar(
                    sector_df,
                    x='Sector',
                    y='Value',
                    title="Portfolio Value by Sector"
                )
                st.plotly_chart(fig_sector, use_container_width=True)

    elif page == "Economic Indicators":
        st.header("📈 Economic Indicators")
        st.info("Economic indicators will be available once GSO data collection is fixed.")

        # Placeholder for economic indicators
        st.subheader("Vietnam Economic Overview")

        # Mock data for demonstration
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("GDP Growth", "5.2%", "0.3%")
        with col2:
            st.metric("Inflation Rate", "3.1%", "-0.2%")
        with col3:
            st.metric("VND/USD", "24,150", "+50")

    # Footer
    st.markdown("---")
    st.markdown("Vietnam Stock Analysis System | Data updated regularly")

if __name__ == "__main__":
    main()