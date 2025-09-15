#!/usr/bin/env python3
"""
Advanced Stock Analyzer for Vietnam Market
- 52-week movement pattern analysis
- Market maker and big money tracking
- Automated stock commentary and behavior analysis
"""

import vnstock as vn
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import statistics

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class AdvancedStockAnalyzer:
    def __init__(self):
        self.vnstock_client = vn.Vnstock()

    def analyze_52_week_patterns(self, symbol: str) -> Dict:
        """Comprehensive 52-week movement pattern analysis"""
        try:
            # Get 52 weeks of data
            end_date = datetime.now()
            start_date = end_date - timedelta(weeks=52)

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'analysis': 'No data available'}

            # Basic price metrics
            current_price = data['close'].iloc[-1]
            week_52_high = data['high'].max()
            week_52_low = data['low'].min()

            # Position within 52-week range
            price_position = (current_price - week_52_low) / (week_52_high - week_52_low) * 100

            # Calculate returns and volatility
            data['daily_return'] = data['close'].pct_change()
            total_return = (current_price / data['close'].iloc[0] - 1) * 100
            volatility = data['daily_return'].std() * np.sqrt(252) * 100  # Annualized

            # Trend analysis
            data['ma_20'] = data['close'].rolling(20).mean()
            data['ma_50'] = data['close'].rolling(50).mean()
            data['ma_200'] = data['close'].rolling(200).mean()

            # Current trend status
            trend_status = self._determine_trend_status(data)

            # Support and resistance levels
            support_resistance = self._find_support_resistance(data)

            # Price momentum patterns
            momentum_analysis = self._analyze_momentum_patterns(data)

            # Seasonal patterns
            seasonal_patterns = self._analyze_seasonal_patterns(data)

            # Trading behavior patterns
            trading_patterns = self._analyze_trading_patterns(data)

            return {
                'symbol': symbol,
                'price_metrics': {
                    'current_price': current_price,
                    '52_week_high': week_52_high,
                    '52_week_low': week_52_low,
                    'position_in_range': price_position,
                    'distance_from_high': (week_52_high - current_price) / week_52_high * 100,
                    'distance_from_low': (current_price - week_52_low) / week_52_low * 100
                },
                'performance': {
                    'total_return_52w': total_return,
                    'annualized_volatility': volatility,
                    'sharpe_ratio': total_return / volatility if volatility > 0 else 0,
                    'max_drawdown': self._calculate_max_drawdown(data)
                },
                'trend_analysis': trend_status,
                'support_resistance': support_resistance,
                'momentum': momentum_analysis,
                'seasonal_patterns': seasonal_patterns,
                'trading_patterns': trading_patterns,
                'commentary': self._generate_52w_commentary(
                    current_price, week_52_high, week_52_low, price_position,
                    total_return, trend_status, momentum_analysis
                )
            }

        except Exception as e:
            logging.error(f"Error analyzing 52-week patterns for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def track_market_maker_activity(self, symbol: str) -> Dict:
        """Track market maker and big money activities"""
        try:
            # Get detailed intraday and recent data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=30)  # Last 30 days for detailed analysis

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'analysis': 'No data available'}

            # Volume analysis
            avg_volume = data['volume'].mean()
            volume_spikes = self._detect_volume_spikes(data)

            # Price-volume relationship analysis
            pv_analysis = self._analyze_price_volume_relationship(data)

            # Large block detection (proxy analysis)
            large_blocks = self._detect_large_block_trading(data)

            # Accumulation/Distribution patterns
            accumulation_distribution = self._analyze_accumulation_distribution(data)

            # Market maker patterns
            mm_patterns = self._detect_market_maker_patterns(data)

            # Foreign vs domestic money flow (proxy analysis)
            money_flow = self._analyze_money_flow_patterns(data)

            # Big money behavior indicators
            big_money_indicators = self._detect_big_money_behavior(data)

            return {
                'symbol': symbol,
                'volume_analysis': {
                    'avg_daily_volume': avg_volume,
                    'volume_spikes': volume_spikes,
                    'volume_trend': 'Increasing' if data['volume'].tail(5).mean() > data['volume'].head(5).mean() else 'Decreasing'
                },
                'price_volume_relationship': pv_analysis,
                'large_block_activity': large_blocks,
                'accumulation_distribution': accumulation_distribution,
                'market_maker_patterns': mm_patterns,
                'money_flow_analysis': money_flow,
                'big_money_indicators': big_money_indicators,
                'commentary': self._generate_big_money_commentary(
                    volume_spikes, large_blocks, accumulation_distribution, big_money_indicators
                )
            }

        except Exception as e:
            logging.error(f"Error tracking market maker activity for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def _determine_trend_status(self, data: pd.DataFrame) -> Dict:
        """Determine current trend status"""
        latest = data.iloc[-1]

        trend_signals = {
            'short_term': 'Bullish' if latest['close'] > latest['ma_20'] else 'Bearish',
            'medium_term': 'Bullish' if latest['close'] > latest['ma_50'] else 'Bearish',
            'long_term': 'Bullish' if latest['close'] > latest['ma_200'] else 'Bearish'
        }

        # Moving average alignment
        ma_alignment = 'Bullish' if latest['ma_20'] > latest['ma_50'] > latest['ma_200'] else 'Bearish'

        return {
            'trend_signals': trend_signals,
            'ma_alignment': ma_alignment,
            'overall_trend': 'Bullish' if sum(1 for t in trend_signals.values() if t == 'Bullish') >= 2 else 'Bearish'
        }

    def _find_support_resistance(self, data: pd.DataFrame) -> Dict:
        """Find key support and resistance levels"""
        # Simple pivot point method
        highs = data['high'].rolling(window=20, center=True).max()
        lows = data['low'].rolling(window=20, center=True).min()

        resistance_levels = data[data['high'] == highs]['high'].unique()
        support_levels = data[data['low'] == lows]['low'].unique()

        current_price = data['close'].iloc[-1]

        return {
            'nearest_resistance': min([r for r in resistance_levels if r > current_price], default=None),
            'nearest_support': max([s for s in support_levels if s < current_price], default=None),
            'key_resistance_levels': sorted(resistance_levels[-3:], reverse=True),
            'key_support_levels': sorted(support_levels[-3:], reverse=True)
        }

    def _analyze_momentum_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze price momentum patterns"""
        # RSI calculation
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        # MACD calculation
        ema_12 = data['close'].ewm(span=12).mean()
        ema_26 = data['close'].ewm(span=26).mean()
        macd = ema_12 - ema_26
        signal_line = macd.ewm(span=9).mean()

        current_rsi = rsi.iloc[-1]
        current_macd = macd.iloc[-1]
        current_signal = signal_line.iloc[-1]

        return {
            'rsi': {
                'current': current_rsi,
                'status': 'Overbought' if current_rsi > 70 else 'Oversold' if current_rsi < 30 else 'Neutral'
            },
            'macd': {
                'macd': current_macd,
                'signal': current_signal,
                'status': 'Bullish' if current_macd > current_signal else 'Bearish'
            },
            'momentum_score': (current_rsi / 100 + (1 if current_macd > current_signal else 0)) / 2 * 100
        }

    def _analyze_seasonal_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze seasonal trading patterns"""
        data['month'] = pd.to_datetime(data.index).month
        data['day_of_week'] = pd.to_datetime(data.index).dayofweek

        monthly_returns = data.groupby('month')['daily_return'].mean() * 100
        weekly_returns = data.groupby('day_of_week')['daily_return'].mean() * 100

        return {
            'best_month': monthly_returns.idxmax(),
            'worst_month': monthly_returns.idxmin(),
            'best_day_of_week': weekly_returns.idxmax(),
            'monthly_patterns': monthly_returns.to_dict(),
            'weekly_patterns': weekly_returns.to_dict()
        }

    def _analyze_trading_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze general trading patterns"""
        # Calculate average true range for volatility
        data['high_low'] = data['high'] - data['low']
        data['high_close'] = abs(data['high'] - data['close'].shift())
        data['low_close'] = abs(data['low'] - data['close'].shift())
        data['atr'] = data[['high_low', 'high_close', 'low_close']].max(axis=1).rolling(14).mean()

        # Trading frequency
        trading_days = len(data[data['volume'] > 0])
        total_days = len(data)

        return {
            'trading_frequency': trading_days / total_days * 100,
            'avg_true_range': data['atr'].iloc[-1],
            'volatility_regime': 'High' if data['atr'].iloc[-1] > data['atr'].mean() else 'Low',
            'consistent_volume': data['volume'].std() / data['volume'].mean() < 1  # Low relative variation
        }

    def _calculate_max_drawdown(self, data: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        cumulative = (1 + data['daily_return'].fillna(0)).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        return drawdown.min() * 100

    def _detect_volume_spikes(self, data: pd.DataFrame) -> List:
        """Detect significant volume spikes"""
        avg_volume = data['volume'].rolling(20).mean()
        volume_ratio = data['volume'] / avg_volume

        spikes = data[volume_ratio > 2.0].copy()  # Volume >200% of average
        spikes['volume_ratio'] = volume_ratio

        spike_list = []
        for idx, row in spikes.tail(10).iterrows():  # Last 10 spikes
            spike_list.append({
                'date': idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx),
                'volume': row['volume'],
                'volume_ratio': row['volume_ratio'],
                'price_change': (row['close'] - row['open']) / row['open'] * 100
            })

        return spike_list

    def _analyze_price_volume_relationship(self, data: pd.DataFrame) -> Dict:
        """Analyze price-volume relationship patterns"""
        # Calculate price change and volume change
        data['price_change'] = data['close'].pct_change()
        data['volume_change'] = data['volume'].pct_change()

        # Correlation between price and volume
        correlation = data['price_change'].corr(data['volume_change'])

        # Volume confirmation patterns
        up_days = data[data['price_change'] > 0]
        down_days = data[data['price_change'] < 0]

        avg_volume_up = up_days['volume'].mean()
        avg_volume_down = down_days['volume'].mean()

        return {
            'price_volume_correlation': correlation,
            'volume_on_up_days': avg_volume_up,
            'volume_on_down_days': avg_volume_down,
            'volume_confirmation': 'Strong' if avg_volume_up > avg_volume_down * 1.2 else 'Weak',
            'pattern': 'Healthy' if correlation > 0.3 and avg_volume_up > avg_volume_down else 'Concerning'
        }

    def _detect_large_block_trading(self, data: pd.DataFrame) -> Dict:
        """Detect large block trading activity (proxy method)"""
        # Use volume and price movement as proxies for block trading
        avg_volume = data['volume'].mean()
        large_volume_days = data[data['volume'] > avg_volume * 2]

        block_trades = []
        for idx, row in large_volume_days.tail(5).iterrows():
            price_impact = abs((row['close'] - row['open']) / row['open'] * 100)
            block_trades.append({
                'date': idx.strftime('%Y-%m-%d') if hasattr(idx, 'strftime') else str(idx),
                'volume': row['volume'],
                'price_impact': price_impact,
                'direction': 'Buy' if row['close'] > row['open'] else 'Sell',
                'likely_institutional': price_impact < 2 and row['volume'] > avg_volume * 3  # Large volume, small impact
            })

        institutional_activity = sum(1 for trade in block_trades if trade['likely_institutional'])

        return {
            'recent_block_trades': block_trades,
            'institutional_activity_score': institutional_activity / len(block_trades) * 100 if block_trades else 0,
            'analysis': 'High institutional activity' if institutional_activity >= 3 else 'Low institutional activity'
        }

    def _analyze_accumulation_distribution(self, data: pd.DataFrame) -> Dict:
        """Analyze accumulation/distribution patterns"""
        # Accumulation/Distribution Line calculation
        data['money_flow_multiplier'] = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
        data['money_flow_multiplier'] = data['money_flow_multiplier'].fillna(0)
        data['money_flow_volume'] = data['money_flow_multiplier'] * data['volume']
        data['ad_line'] = data['money_flow_volume'].cumsum()

        # Trend of A/D line
        ad_trend = 'Accumulation' if data['ad_line'].iloc[-1] > data['ad_line'].iloc[-10] else 'Distribution'

        # On Balance Volume
        data['obv'] = (data['volume'] * ((data['close'] > data['close'].shift()).astype(int) * 2 - 1)).cumsum()
        obv_trend = 'Bullish' if data['obv'].iloc[-1] > data['obv'].iloc[-10] else 'Bearish'

        return {
            'accumulation_distribution_trend': ad_trend,
            'obv_trend': obv_trend,
            'current_ad_line': data['ad_line'].iloc[-1],
            'ad_line_change_10d': data['ad_line'].iloc[-1] - data['ad_line'].iloc[-10],
            'pattern': 'Strong Hands Accumulating' if ad_trend == 'Accumulation' and obv_trend == 'Bullish' else 'Weak Hands Distributing'
        }

    def _detect_market_maker_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect potential market maker patterns"""
        # Calculate intraday ranges and patterns
        data['daily_range'] = (data['high'] - data['low']) / data['close'] * 100
        data['body_ratio'] = abs(data['close'] - data['open']) / (data['high'] - data['low'])

        avg_range = data['daily_range'].mean()
        avg_body_ratio = data['body_ratio'].mean()

        # Look for patterns that suggest market making activity
        tight_spreads = len(data[data['daily_range'] < avg_range * 0.7]) / len(data) * 100
        small_bodies = len(data[data['body_ratio'] < 0.3]) / len(data) * 100

        return {
            'average_daily_range': avg_range,
            'tight_spread_days': tight_spreads,
            'small_body_days': small_bodies,
            'market_maker_activity': 'High' if tight_spreads > 30 and small_bodies > 40 else 'Moderate' if tight_spreads > 20 else 'Low',
            'liquidity_provision': 'Good' if tight_spreads > 25 else 'Poor'
        }

    def _analyze_money_flow_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze money flow patterns (proxy for foreign vs domestic)"""
        # Use time-based analysis as proxy (foreign investors often trade at different times)
        data['hour'] = pd.to_datetime(data.index).hour if hasattr(data.index, 'hour') else 9  # Default market hours

        # Volume-weighted analysis
        recent_data = data.tail(10)
        high_volume_days = recent_data[recent_data['volume'] > recent_data['volume'].mean()]

        net_buying_pressure = 0
        for _, row in high_volume_days.iterrows():
            if row['close'] > row['open']:
                net_buying_pressure += row['volume']
            else:
                net_buying_pressure -= row['volume']

        return {
            'net_buying_pressure': 'Positive' if net_buying_pressure > 0 else 'Negative',
            'foreign_activity_proxy': 'High' if len(high_volume_days) > 5 else 'Moderate',
            'money_flow_trend': 'Inflow' if net_buying_pressure > 0 else 'Outflow',
            'strength': abs(net_buying_pressure) / recent_data['volume'].sum() * 100
        }

    def _detect_big_money_behavior(self, data: pd.DataFrame) -> Dict:
        """Detect big money behavior patterns"""
        # Large volume with minimal price impact (institutional trading)
        data['volume_price_efficiency'] = data['volume'] / abs(data['close'].pct_change().fillna(0) * 100 + 0.01)

        efficient_trading_days = len(data[data['volume_price_efficiency'] > data['volume_price_efficiency'].quantile(0.8)])

        # Consistent accumulation patterns
        recent_closes = data['close'].tail(10)
        upward_bias = len(recent_closes[recent_closes > recent_closes.median()]) / len(recent_closes)

        # Smart money indicators
        smart_money_score = 0
        if efficient_trading_days > 5:
            smart_money_score += 30
        if upward_bias > 0.6:
            smart_money_score += 25
        if data['obv'].iloc[-1] > data['obv'].iloc[-20]:  # Need OBV from previous calculation
            smart_money_score += 25

        return {
            'efficient_trading_days': efficient_trading_days,
            'upward_bias': upward_bias * 100,
            'smart_money_score': smart_money_score,
            'big_money_activity': 'High' if smart_money_score > 60 else 'Moderate' if smart_money_score > 30 else 'Low',
            'institutional_interest': 'Strong' if efficient_trading_days > 7 and upward_bias > 0.7 else 'Weak'
        }

    def _generate_52w_commentary(self, current_price, high_52w, low_52w, position, total_return, trend, momentum) -> str:
        """Generate automated commentary for 52-week analysis"""
        commentary = []

        # Position analysis
        if position > 80:
            commentary.append(f"Trading near 52-week highs ({position:.1f}% of range)")
        elif position < 20:
            commentary.append(f"Trading near 52-week lows ({position:.1f}% of range)")
        else:
            commentary.append(f"Trading in middle of 52-week range ({position:.1f}%)")

        # Performance commentary
        if total_return > 20:
            commentary.append(f"Strong performer with {total_return:.1f}% annual return")
        elif total_return < -20:
            commentary.append(f"Underperformer with {total_return:.1f}% annual decline")
        else:
            commentary.append(f"Moderate performance with {total_return:.1f}% return")

        # Trend commentary
        commentary.append(f"Overall trend is {trend['overall_trend'].lower()}")

        # Momentum commentary
        rsi_status = momentum['rsi']['status']
        if rsi_status != 'Neutral':
            commentary.append(f"RSI suggests {rsi_status.lower()} conditions")

        return ". ".join(commentary) + "."

    def _generate_big_money_commentary(self, volume_spikes, large_blocks, accumulation, big_money) -> str:
        """Generate automated commentary for big money analysis"""
        commentary = []

        # Volume activity
        if len(volume_spikes) > 3:
            commentary.append("High volume activity detected in recent sessions")

        # Institutional activity
        institutional_score = large_blocks.get('institutional_activity_score', 0)
        if institutional_score > 50:
            commentary.append("Strong institutional trading presence")
        elif institutional_score > 20:
            commentary.append("Moderate institutional interest")

        # Accumulation/Distribution
        pattern = accumulation.get('pattern', '')
        if 'Accumulating' in pattern:
            commentary.append("Smart money appears to be accumulating")
        elif 'Distributing' in pattern:
            commentary.append("Signs of distribution by informed traders")

        # Big money behavior
        big_money_activity = big_money.get('big_money_activity', 'Low')
        commentary.append(f"{big_money_activity.lower()} big money activity level")

        return ". ".join(commentary) + "." if commentary else "Limited big money activity detected."

    def generate_comprehensive_analysis(self, symbol: str) -> Dict:
        """Generate comprehensive analysis combining all methods"""
        logging.info(f"Generating comprehensive analysis for {symbol}")

        analysis = {
            'symbol': symbol,
            'analysis_date': datetime.now().isoformat(),
            'pattern_analysis': self.analyze_52_week_patterns(symbol),
            'market_maker_analysis': self.track_market_maker_activity(symbol)
        }

        # Generate executive summary
        pattern_data = analysis['pattern_analysis']
        mm_data = analysis['market_maker_analysis']

        if 'error' not in pattern_data and 'error' not in mm_data:
            analysis['executive_summary'] = {
                'investment_grade': self._determine_investment_grade(pattern_data, mm_data),
                'key_insights': self._extract_key_insights(pattern_data, mm_data),
                'risk_factors': self._identify_risk_factors(pattern_data, mm_data),
                'opportunity_score': self._calculate_opportunity_score(pattern_data, mm_data)
            }

        return analysis

    def _determine_investment_grade(self, pattern_data: Dict, mm_data: Dict) -> str:
        """Determine overall investment grade"""
        score = 0

        # Pattern analysis scoring
        if pattern_data.get('trend_analysis', {}).get('overall_trend') == 'Bullish':
            score += 25
        if pattern_data.get('price_metrics', {}).get('position_in_range', 0) > 60:
            score += 15
        if pattern_data.get('performance', {}).get('total_return_52w', 0) > 10:
            score += 20

        # Market maker analysis scoring
        if mm_data.get('big_money_indicators', {}).get('big_money_activity') == 'High':
            score += 25
        if mm_data.get('accumulation_distribution', {}).get('pattern', '') == 'Strong Hands Accumulating':
            score += 15

        if score >= 75:
            return 'A - Strong Buy'
        elif score >= 60:
            return 'B - Buy'
        elif score >= 40:
            return 'C - Hold'
        elif score >= 25:
            return 'D - Weak Hold'
        else:
            return 'F - Sell'

    def _extract_key_insights(self, pattern_data: Dict, mm_data: Dict) -> List[str]:
        """Extract key insights from analysis"""
        insights = []

        # From pattern analysis
        position = pattern_data.get('price_metrics', {}).get('position_in_range', 0)
        if position > 80:
            insights.append("Stock trading near 52-week highs - momentum play")
        elif position < 20:
            insights.append("Stock near 52-week lows - potential value opportunity")

        # From market maker analysis
        big_money = mm_data.get('big_money_indicators', {}).get('big_money_activity', 'Low')
        if big_money == 'High':
            insights.append("High institutional interest detected")

        accumulation = mm_data.get('accumulation_distribution', {}).get('pattern', '')
        if 'Accumulating' in accumulation:
            insights.append("Smart money accumulation pattern identified")

        return insights

    def _identify_risk_factors(self, pattern_data: Dict, mm_data: Dict) -> List[str]:
        """Identify key risk factors"""
        risks = []

        # Volatility risk
        volatility = pattern_data.get('performance', {}).get('annualized_volatility', 0)
        if volatility > 40:
            risks.append("High volatility - suitable for risk-tolerant investors")

        # Liquidity risk
        volume_confirmation = mm_data.get('price_volume_relationship', {}).get('volume_confirmation', '')
        if volume_confirmation == 'Weak':
            risks.append("Weak volume confirmation - liquidity concerns")

        # Trend risk
        trend = pattern_data.get('trend_analysis', {}).get('overall_trend', '')
        if trend == 'Bearish':
            risks.append("Bearish trend - downside momentum risk")

        return risks

    def _calculate_opportunity_score(self, pattern_data: Dict, mm_data: Dict) -> int:
        """Calculate overall opportunity score (0-100)"""
        score = 50  # Base score

        # Technical factors
        if pattern_data.get('trend_analysis', {}).get('overall_trend') == 'Bullish':
            score += 15
        if pattern_data.get('momentum', {}).get('momentum_score', 0) > 60:
            score += 10

        # Fundamental proxy factors
        if pattern_data.get('performance', {}).get('total_return_52w', 0) > 15:
            score += 15

        # Market structure factors
        if mm_data.get('big_money_indicators', {}).get('smart_money_score', 0) > 60:
            score += 15

        # Penalty factors
        if pattern_data.get('performance', {}).get('annualized_volatility', 0) > 50:
            score -= 15

        return max(0, min(100, score))

if __name__ == "__main__":
    analyzer = AdvancedStockAnalyzer()

    # Test with a sample stock
    test_symbol = "VCB"
    analysis = analyzer.generate_comprehensive_analysis(test_symbol)

    print(f"📊 COMPREHENSIVE ANALYSIS: {test_symbol}")
    print("=" * 50)

    if 'executive_summary' in analysis:
        summary = analysis['executive_summary']
        print(f"Investment Grade: {summary['investment_grade']}")
        print(f"Opportunity Score: {summary['opportunity_score']}/100")
        print(f"\nKey Insights:")
        for insight in summary['key_insights']:
            print(f"• {insight}")
        print(f"\nRisk Factors:")
        for risk in summary['risk_factors']:
            print(f"⚠ {risk}")

    # Save full analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'/workspaces/BMAD-METHOD/session_logs/comprehensive_analysis_{test_symbol}_{timestamp}.json'

    with open(filename, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"\n💾 Full analysis saved to: {filename}")
    print("🚀 Advanced stock analysis system ready!")