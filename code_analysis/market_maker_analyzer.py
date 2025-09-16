#!/usr/bin/env python3
"""
Market Maker Analysis System for Vietnam Stocks
Provides deep insights into market maker behavior, smart money flow,
and institutional trading patterns for individual stocks
"""

import vnstock as vn
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import statistics
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class MarketMakerAnalyzer:
    def __init__(self):
        self.vnstock_client = vn.Vnstock()

        # Market maker behavior patterns
        self.mm_patterns = {
            'accumulation_phase': {
                'volume_increase': True,
                'price_stability': True,
                'volatility_decrease': True,
                'support_building': True
            },
            'distribution_phase': {
                'volume_increase': True,
                'price_instability': True,
                'volatility_increase': True,
                'resistance_testing': True
            },
            'markup_phase': {
                'volume_confirmation': True,
                'price_breakout': True,
                'momentum_building': True,
                'institutional_buying': True
            }
        }

        # Smart money indicators
        self.smart_money_indicators = {
            'large_block_trades': 'volume_spikes_with_minimal_impact',
            'dark_pool_activity': 'consistent_buying_without_price_impact',
            'institutional_patterns': 'time_based_trading_patterns',
            'informed_trading': 'pre_announcement_accumulation'
        }

    def analyze_market_maker_style(self, symbol: str) -> Dict:
        """Analyze the market making style and behavior for a specific stock"""
        logging.info(f"Analyzing market maker style for {symbol}")

        try:
            # Get extended historical data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)  # 6 months

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'error': 'No data available'}

            # Core market maker analysis
            mm_style = self.identify_mm_style(data)
            smart_money_flow = self.detect_smart_money_flow(data)
            institutional_behavior = self.analyze_institutional_behavior(data)
            liquidity_provision = self.assess_liquidity_provision(data)
            price_discovery = self.analyze_price_discovery_efficiency(data)

            # Market phase identification
            current_phase = self.identify_market_phase(data)

            # Trading patterns
            trading_patterns = self.analyze_trading_patterns(data)

            # Risk assessment
            risk_profile = self.assess_mm_risk_profile(data)

            return {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'market_maker_style': mm_style,
                'smart_money_analysis': smart_money_flow,
                'institutional_behavior': institutional_behavior,
                'liquidity_provision': liquidity_provision,
                'price_discovery': price_discovery,
                'current_market_phase': current_phase,
                'trading_patterns': trading_patterns,
                'risk_profile': risk_profile,
                'actionable_insights': self.generate_actionable_insights(
                    mm_style, smart_money_flow, current_phase, risk_profile
                ),
                'entry_exit_signals': self.generate_entry_exit_signals(data, current_phase, smart_money_flow)
            }

        except Exception as e:
            logging.error(f"Error analyzing market maker style for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def identify_mm_style(self, data: pd.DataFrame) -> Dict:
        """Identify the market maker's operational style"""

        # Calculate key metrics
        daily_ranges = (data['high'] - data['low']) / data['close'] * 100
        intraday_reversals = abs(data['close'] - data['open']) / (data['high'] - data['low'])
        volume_consistency = data['volume'].std() / data['volume'].mean()

        # Price stability analysis
        price_volatility = data['close'].pct_change().std() * np.sqrt(252) * 100
        bid_ask_proxy = daily_ranges.mean()  # Using daily range as bid-ask spread proxy

        # Style classification
        if bid_ask_proxy < 2 and volume_consistency < 0.8:
            mm_style = "Professional Market Maker"
            characteristics = ["Tight spreads", "Consistent liquidity", "Low volatility"]
            aggression_level = "Conservative"
        elif bid_ask_proxy < 3 and volume_consistency < 1.2:
            mm_style = "Active Liquidity Provider"
            characteristics = ["Moderate spreads", "Good liquidity", "Moderate volatility"]
            aggression_level = "Moderate"
        else:
            mm_style = "Opportunistic Trader"
            characteristics = ["Wide spreads", "Inconsistent liquidity", "High volatility"]
            aggression_level = "Aggressive"

        return {
            'style_classification': mm_style,
            'characteristics': characteristics,
            'aggression_level': aggression_level,
            'metrics': {
                'avg_daily_range': bid_ask_proxy,
                'volume_consistency': volume_consistency,
                'price_volatility': price_volatility,
                'intraday_reversal_rate': intraday_reversals.mean()
            },
            'efficiency_score': self.calculate_mm_efficiency_score(
                bid_ask_proxy, volume_consistency, price_volatility
            )
        }

    def detect_smart_money_flow(self, data: pd.DataFrame) -> Dict:
        """Detect smart money flow patterns"""

        # Volume-weighted analysis
        data['volume_ma'] = data['volume'].rolling(20).mean()
        data['price_change'] = data['close'].pct_change()

        # Large block detection
        volume_threshold = data['volume'].quantile(0.8)  # Top 20% volume days
        large_volume_days = data[data['volume'] > volume_threshold].copy()

        # Smart money indicators
        smart_money_score = 0
        indicators = {}

        # 1. Large volume with minimal price impact
        if not large_volume_days.empty:
            large_volume_days['price_impact'] = abs(large_volume_days['price_change']) * 100
            low_impact_trades = large_volume_days[large_volume_days['price_impact'] < 2]

            indicators['stealth_accumulation'] = {
                'count': len(low_impact_trades),
                'percentage': len(low_impact_trades) / len(large_volume_days) * 100,
                'avg_volume': low_impact_trades['volume'].mean(),
                'score': min(100, len(low_impact_trades) * 10)
            }
            smart_money_score += indicators['stealth_accumulation']['score'] * 0.3

        # 2. Consistent buying patterns
        data['obv'] = (data['volume'] * np.sign(data['price_change'])).cumsum()
        obv_trend = data['obv'].tail(30).corr(pd.Series(range(30)))

        indicators['accumulation_trend'] = {
            'obv_trend_correlation': obv_trend,
            'trend_strength': 'Strong' if abs(obv_trend) > 0.7 else 'Moderate' if abs(obv_trend) > 0.4 else 'Weak',
            'direction': 'Bullish' if obv_trend > 0 else 'Bearish',
            'score': max(0, abs(obv_trend) * 100)
        }
        smart_money_score += indicators['accumulation_trend']['score'] * 0.3

        # 3. Volume-price divergence analysis
        recent_price_trend = data['close'].tail(20).corr(pd.Series(range(20)))
        recent_volume_trend = data['volume'].tail(20).corr(pd.Series(range(20)))

        divergence = abs(recent_price_trend - recent_volume_trend)
        indicators['volume_price_divergence'] = {
            'price_trend': recent_price_trend,
            'volume_trend': recent_volume_trend,
            'divergence_score': divergence,
            'interpretation': self.interpret_vp_divergence(recent_price_trend, recent_volume_trend),
            'score': max(0, (1 - divergence) * 100) if divergence < 1 else 0
        }
        smart_money_score += indicators['volume_price_divergence']['score'] * 0.2

        # 4. Institutional time patterns (proxy)
        data['hour'] = 9  # Placeholder for hour analysis
        morning_volume = data['volume'].head(len(data)//2).mean()
        afternoon_volume = data['volume'].tail(len(data)//2).mean()

        indicators['time_pattern_analysis'] = {
            'morning_avg_volume': morning_volume,
            'afternoon_avg_volume': afternoon_volume,
            'institutional_bias': 'Morning' if morning_volume > afternoon_volume * 1.2 else 'Balanced',
            'score': 70 if morning_volume > afternoon_volume * 1.2 else 50
        }
        smart_money_score += indicators['time_pattern_analysis']['score'] * 0.2

        return {
            'smart_money_score': min(100, smart_money_score),
            'flow_direction': 'Inflow' if smart_money_score > 60 else 'Neutral' if smart_money_score > 40 else 'Outflow',
            'confidence_level': 'High' if smart_money_score > 70 else 'Medium' if smart_money_score > 50 else 'Low',
            'indicators': indicators,
            'summary': self.generate_smart_money_summary(smart_money_score, indicators)
        }

    def analyze_institutional_behavior(self, data: pd.DataFrame) -> Dict:
        """Analyze institutional trading behavior patterns"""

        # Institutional characteristics
        data['returns'] = data['close'].pct_change()

        # 1. Persistence analysis (institutions tend to trade consistently)
        return_autocorr = data['returns'].autocorr(lag=1)
        volume_autocorr = data['volume'].pct_change().autocorr(lag=1)

        # 2. Large trade frequency
        median_volume = data['volume'].median()
        large_trades = len(data[data['volume'] > median_volume * 2]) / len(data) * 100

        # 3. Price efficiency (institutions improve price discovery)
        price_changes = data['close'].pct_change().abs()
        volume_weighted_changes = (price_changes * data['volume']).sum() / data['volume'].sum()

        # 4. Momentum persistence (institutional herding)
        momentum_periods = self.identify_momentum_periods(data)

        institutional_score = 50  # Base score

        # Scoring logic
        if abs(return_autocorr) > 0.1:
            institutional_score += 15
        if large_trades > 25:
            institutional_score += 15
        if volume_weighted_changes < price_changes.mean():
            institutional_score += 10
        if len(momentum_periods) > 2:
            institutional_score += 10

        return {
            'institutional_activity_score': min(100, institutional_score),
            'activity_level': 'High' if institutional_score > 70 else 'Medium' if institutional_score > 50 else 'Low',
            'behavior_patterns': {
                'return_persistence': return_autocorr,
                'volume_persistence': volume_autocorr,
                'large_trade_frequency': large_trades,
                'price_efficiency_metric': volume_weighted_changes,
                'momentum_periods': len(momentum_periods)
            },
            'trading_style': self.classify_institutional_style(institutional_score, return_autocorr, large_trades),
            'impact_assessment': self.assess_institutional_impact(data)
        }

    def assess_liquidity_provision(self, data: pd.DataFrame) -> Dict:
        """Assess the quality of liquidity provision"""

        # Liquidity metrics
        daily_turnover = data['volume'] * data['close']
        avg_turnover = daily_turnover.mean()
        turnover_consistency = daily_turnover.std() / avg_turnover

        # Spread proxy (using daily range)
        effective_spread = (data['high'] - data['low']) / data['close']
        avg_spread = effective_spread.mean() * 100

        # Market depth proxy (volume at different price levels)
        price_impact = abs(data['close'].pct_change()) / (data['volume'] / data['volume'].mean())
        avg_price_impact = price_impact.mean()

        # Liquidity score calculation
        liquidity_score = 100 - min(100, avg_spread * 10 + turnover_consistency * 20 + avg_price_impact * 1000)
        liquidity_score = max(0, liquidity_score)

        return {
            'liquidity_score': liquidity_score,
            'liquidity_grade': self.grade_liquidity(liquidity_score),
            'metrics': {
                'average_daily_turnover': avg_turnover,
                'turnover_consistency': turnover_consistency,
                'effective_spread_pct': avg_spread,
                'price_impact_coefficient': avg_price_impact
            },
            'provision_quality': {
                'consistency': 'High' if turnover_consistency < 0.5 else 'Medium' if turnover_consistency < 1.0 else 'Low',
                'depth': 'Deep' if avg_price_impact < 0.001 else 'Moderate' if avg_price_impact < 0.005 else 'Shallow',
                'spread_tightness': 'Tight' if avg_spread < 1 else 'Moderate' if avg_spread < 2 else 'Wide'
            }
        }

    def analyze_price_discovery_efficiency(self, data: pd.DataFrame) -> Dict:
        """Analyze price discovery efficiency"""

        # Random walk test (efficient market)
        returns = data['close'].pct_change().dropna()

        # Variance ratio test
        def variance_ratio_test(returns, k=2):
            n = len(returns)
            mu = returns.mean()

            # Variance of k-period returns
            k_returns = returns.rolling(k).sum().dropna()
            var_k = k_returns.var()

            # Variance of 1-period returns
            var_1 = returns.var()

            # Variance ratio
            vr = var_k / (k * var_1)
            return vr

        vr_2 = variance_ratio_test(returns, 2)
        vr_4 = variance_ratio_test(returns, 4)

        # Price efficiency score
        efficiency_score = 100 - abs(vr_2 - 1) * 100 - abs(vr_4 - 1) * 50
        efficiency_score = max(0, efficiency_score)

        # Autocorrelation analysis
        return_autocorr = returns.autocorr()

        return {
            'efficiency_score': efficiency_score,
            'efficiency_grade': self.grade_efficiency(efficiency_score),
            'variance_ratios': {
                '2_period': vr_2,
                '4_period': vr_4
            },
            'return_autocorrelation': return_autocorr,
            'market_microstructure': {
                'price_discovery_quality': 'High' if efficiency_score > 80 else 'Medium' if efficiency_score > 60 else 'Low',
                'information_incorporation': 'Fast' if abs(return_autocorr) < 0.05 else 'Slow',
                'market_maturity': 'Mature' if efficiency_score > 70 and abs(return_autocorr) < 0.1 else 'Developing'
            }
        }

    def identify_market_phase(self, data: pd.DataFrame) -> Dict:
        """Identify current market phase"""

        # Technical indicators for phase identification
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['volume_sma'] = data['volume'].rolling(20).mean()

        latest = data.iloc[-1]
        recent_data = data.tail(20)

        # Phase indicators
        price_trend = (latest['close'] - data['close'].iloc[-30]) / data['close'].iloc[-30]
        volume_trend = (latest['volume'] - data['volume'].iloc[-30]) / data['volume'].iloc[-30]
        volatility = recent_data['close'].pct_change().std()

        # Phase classification logic
        if price_trend > 0.05 and volume_trend > 0.2 and volatility < 0.03:
            phase = "Accumulation"
            characteristics = ["Rising prices", "Increasing volume", "Low volatility"]
            mm_behavior = "Supporting prices, providing liquidity"
        elif price_trend > 0.1 and volume_trend > 0.5:
            phase = "Markup"
            characteristics = ["Strong price increase", "High volume", "Momentum building"]
            mm_behavior = "Facilitating breakout, reducing resistance"
        elif price_trend < -0.05 and volume_trend > 0.3:
            phase = "Distribution"
            characteristics = ["Declining prices", "High volume", "Institutional selling"]
            mm_behavior = "Absorbing selling pressure"
        elif abs(price_trend) < 0.02 and volatility < 0.02:
            phase = "Consolidation"
            characteristics = ["Sideways price action", "Low volatility", "Range-bound"]
            mm_behavior = "Maintaining tight spreads, range trading"
        else:
            phase = "Transition"
            characteristics = ["Mixed signals", "Uncertain direction", "Variable volume"]
            mm_behavior = "Adapting to changing conditions"

        return {
            'current_phase': phase,
            'phase_characteristics': characteristics,
            'mm_expected_behavior': mm_behavior,
            'phase_metrics': {
                'price_trend_30d': price_trend * 100,
                'volume_trend_30d': volume_trend * 100,
                'recent_volatility': volatility * 100
            },
            'phase_strength': self.assess_phase_strength(price_trend, volume_trend, volatility),
            'expected_duration': self.estimate_phase_duration(phase, data)
        }

    def generate_actionable_insights(self, mm_style: Dict, smart_money: Dict, phase: Dict, risk: Dict) -> Dict:
        """Generate actionable trading insights"""

        insights = {
            'primary_opportunity': '',
            'risk_considerations': [],
            'timing_factors': [],
            'position_sizing': '',
            'trade_management': []
        }

        # Primary opportunity identification
        if smart_money['flow_direction'] == 'Inflow' and phase['current_phase'] == 'Accumulation':
            insights['primary_opportunity'] = 'Strong accumulation by smart money - consider building position'
        elif phase['current_phase'] == 'Markup' and mm_style['efficiency_score'] > 70:
            insights['primary_opportunity'] = 'Efficient market maker supporting uptrend - momentum play'
        elif smart_money['flow_direction'] == 'Outflow' and phase['current_phase'] == 'Distribution':
            insights['primary_opportunity'] = 'Distribution detected - avoid or consider short position'
        else:
            insights['primary_opportunity'] = 'Mixed signals - wait for clearer opportunity'

        # Risk considerations
        if risk.get('volatility_regime') == 'High':
            insights['risk_considerations'].append('High volatility environment - use smaller position sizes')
        if mm_style['aggression_level'] == 'Aggressive':
            insights['risk_considerations'].append('Aggressive market maker - expect wider spreads')
        if smart_money['confidence_level'] == 'Low':
            insights['risk_considerations'].append('Unclear smart money direction - monitor closely')

        # Timing factors
        if phase['current_phase'] in ['Accumulation', 'Consolidation']:
            insights['timing_factors'].append('Patient entry approach - look for confirmation')
        if phase['current_phase'] == 'Markup':
            insights['timing_factors'].append('Momentum-based timing - enter on pullbacks')

        return insights

    def generate_entry_exit_signals(self, data: pd.DataFrame, phase: Dict, smart_money: Dict) -> Dict:
        """Generate specific entry and exit signals"""

        # Calculate technical levels
        recent_high = data['high'].tail(20).max()
        recent_low = data['low'].tail(20).min()
        current_price = data['close'].iloc[-1]

        # Volume analysis
        avg_volume = data['volume'].tail(20).mean()
        current_volume = data['volume'].iloc[-1]

        signals = {
            'entry_signals': [],
            'exit_signals': [],
            'stop_loss_level': recent_low * 0.95,  # 5% below recent low
            'target_levels': [],
            'signal_strength': 'Weak'
        }

        # Entry signals based on phase and smart money
        if phase['current_phase'] == 'Accumulation' and smart_money['flow_direction'] == 'Inflow':
            signals['entry_signals'].append({
                'signal': 'Smart money accumulation',
                'trigger': f'Buy on approach to {recent_low * 1.02:.2f}',
                'strength': 'Strong'
            })

        if current_volume > avg_volume * 1.5 and (current_price - data['close'].iloc[-2]) / data['close'].iloc[-2] > 0.02:
            signals['entry_signals'].append({
                'signal': 'Volume breakout',
                'trigger': f'Buy above {current_price:.2f} with volume confirmation',
                'strength': 'Medium'
            })

        # Exit signals
        if phase['current_phase'] == 'Distribution':
            signals['exit_signals'].append({
                'signal': 'Distribution phase detected',
                'trigger': 'Consider profit taking',
                'urgency': 'Medium'
            })

        # Target levels
        price_range = recent_high - recent_low
        signals['target_levels'] = [
            current_price + price_range * 0.5,
            current_price + price_range * 1.0,
            current_price + price_range * 1.618  # Fibonacci extension
        ]

        # Overall signal strength
        signal_count = len(signals['entry_signals'])
        smart_money_score = smart_money.get('smart_money_score', 50)

        if signal_count >= 2 and smart_money_score > 70:
            signals['signal_strength'] = 'Strong'
        elif signal_count >= 1 and smart_money_score > 50:
            signals['signal_strength'] = 'Medium'

        return signals

    def analyze_trading_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze market maker trading patterns"""
        # Calculate average true range for volatility assessment
        data['high_low'] = data['high'] - data['low']
        data['high_close'] = abs(data['high'] - data['close'].shift())
        data['low_close'] = abs(data['low'] - data['close'].shift())
        data['atr'] = data[['high_low', 'high_close', 'low_close']].max(axis=1).rolling(14).mean()

        # Trading frequency
        trading_days = len(data[data['volume'] > 0])
        total_days = len(data)

        # Price consistency (measure of smooth moves vs gaps)
        price_gaps = abs(data['open'] - data['close'].shift())
        avg_gap = price_gaps.mean()
        avg_range = data['atr'].mean()
        price_consistency = 1 - (avg_gap / avg_range) if avg_range > 0 else 0

        # Volume pattern consistency
        volume_cv = data['volume'].std() / data['volume'].mean() if data['volume'].mean() > 0 else 1

        return {
            'trading_frequency': trading_days / total_days * 100,
            'avg_true_range': data['atr'].iloc[-1] if not data['atr'].isna().iloc[-1] else 0,
            'volatility_regime': 'High' if data['atr'].iloc[-1] > data['atr'].mean() else 'Low',
            'price_consistency': price_consistency,
            'volume_consistency': 'High' if volume_cv < 0.5 else 'Medium' if volume_cv < 1.0 else 'Low',
            'pattern_type': 'Institutional' if price_consistency > 0.7 and volume_cv < 0.8 else 'Retail'
        }

    # Helper methods

    def calculate_mm_efficiency_score(self, spread: float, consistency: float, volatility: float) -> float:
        """Calculate market maker efficiency score"""
        spread_score = max(0, 100 - spread * 20)
        consistency_score = max(0, 100 - consistency * 50)
        volatility_score = max(0, 100 - volatility)

        return (spread_score + consistency_score + volatility_score) / 3

    def interpret_vp_divergence(self, price_trend: float, volume_trend: float) -> str:
        """Interpret volume-price divergence"""
        if price_trend > 0 and volume_trend > 0:
            return "Healthy uptrend with volume support"
        elif price_trend > 0 and volume_trend < 0:
            return "Price up but volume declining - potential weakness"
        elif price_trend < 0 and volume_trend > 0:
            return "Price down with volume - possible accumulation"
        else:
            return "Both price and volume declining - consolidation"

    def identify_momentum_periods(self, data: pd.DataFrame) -> List:
        """Identify periods of sustained momentum"""
        momentum_periods = []
        returns = data['close'].pct_change()

        # Simple momentum identification (3+ consecutive days same direction)
        consecutive_up = 0
        consecutive_down = 0

        for ret in returns:
            if ret > 0.01:  # 1% threshold
                consecutive_up += 1
                consecutive_down = 0
                if consecutive_up >= 3:
                    momentum_periods.append('up')
            elif ret < -0.01:
                consecutive_down += 1
                consecutive_up = 0
                if consecutive_down >= 3:
                    momentum_periods.append('down')
            else:
                consecutive_up = 0
                consecutive_down = 0

        return momentum_periods

    def classify_institutional_style(self, score: float, persistence: float, large_trades: float) -> str:
        """Classify institutional trading style"""
        if score > 70 and abs(persistence) > 0.1:
            return "Systematic/Algorithmic"
        elif large_trades > 30:
            return "Block Trader/Institutional"
        elif score > 50:
            return "Active Professional"
        else:
            return "Retail Dominated"

    def assess_institutional_impact(self, data: pd.DataFrame) -> Dict:
        """Assess institutional impact on price discovery"""
        volume_weighted_price = (data['close'] * data['volume']).sum() / data['volume'].sum()
        simple_avg_price = data['close'].mean()

        impact = abs(volume_weighted_price - simple_avg_price) / simple_avg_price * 100

        return {
            'price_impact_pct': impact,
            'impact_level': 'High' if impact > 2 else 'Medium' if impact > 1 else 'Low',
            'volume_weighted_price': volume_weighted_price,
            'simple_average_price': simple_avg_price
        }

    def grade_liquidity(self, score: float) -> str:
        """Grade liquidity provision quality"""
        if score >= 80: return 'A - Excellent'
        elif score >= 70: return 'B - Good'
        elif score >= 60: return 'C - Average'
        elif score >= 50: return 'D - Below Average'
        else: return 'F - Poor'

    def grade_efficiency(self, score: float) -> str:
        """Grade price discovery efficiency"""
        if score >= 85: return 'A - Highly Efficient'
        elif score >= 75: return 'B - Efficient'
        elif score >= 65: return 'C - Moderately Efficient'
        elif score >= 55: return 'D - Somewhat Inefficient'
        else: return 'F - Inefficient'

    def generate_smart_money_summary(self, score: float, indicators: Dict) -> str:
        """Generate smart money flow summary"""
        if score > 70:
            return "Strong smart money inflows detected with multiple confirmation signals"
        elif score > 50:
            return "Moderate smart money activity with some positive indicators"
        elif score < 30:
            return "Smart money appears to be exiting or avoiding this stock"
        else:
            return "Mixed signals from smart money - no clear direction"

    def assess_phase_strength(self, price_trend: float, volume_trend: float, volatility: float) -> str:
        """Assess the strength of current market phase"""
        if abs(price_trend) > 0.1 and volume_trend > 0.3:
            return "Strong"
        elif abs(price_trend) > 0.05 or volume_trend > 0.2:
            return "Moderate"
        else:
            return "Weak"

    def estimate_phase_duration(self, phase: str, data: pd.DataFrame) -> str:
        """Estimate how long the current phase might last"""
        phase_durations = {
            'Accumulation': '2-8 weeks',
            'Markup': '3-12 weeks',
            'Distribution': '2-6 weeks',
            'Consolidation': '1-4 weeks',
            'Transition': '1-2 weeks'
        }
        return phase_durations.get(phase, 'Unknown')

    def assess_mm_risk_profile(self, data: pd.DataFrame) -> Dict:
        """Assess risk profile of market maker activities"""

        # Calculate various risk metrics
        price_volatility = data['close'].pct_change().std() * np.sqrt(252) * 100
        volume_volatility = data['volume'].pct_change().std() * 100

        # Maximum consecutive days of declining volume
        volume_declines = []
        current_decline = 0
        volume_changes = data['volume'].pct_change()

        for change in volume_changes:
            if change < 0:
                current_decline += 1
            else:
                if current_decline > 0:
                    volume_declines.append(current_decline)
                current_decline = 0

        max_volume_decline_days = max(volume_declines) if volume_declines else 0

        # Risk scoring
        risk_score = 50  # Base

        if price_volatility > 40:
            risk_score += 20
        elif price_volatility > 25:
            risk_score += 10

        if volume_volatility > 100:
            risk_score += 15

        if max_volume_decline_days > 5:
            risk_score += 15

        risk_level = 'High' if risk_score > 70 else 'Medium' if risk_score > 50 else 'Low'

        return {
            'risk_score': min(100, risk_score),
            'risk_level': risk_level,
            'volatility_regime': 'High' if price_volatility > 30 else 'Medium' if price_volatility > 20 else 'Low',
            'liquidity_risk': 'High' if max_volume_decline_days > 7 else 'Medium' if max_volume_decline_days > 3 else 'Low',
            'risk_factors': {
                'price_volatility_annualized': price_volatility,
                'volume_volatility': volume_volatility,
                'max_volume_decline_days': max_volume_decline_days
            }
        }

if __name__ == "__main__":
    analyzer = MarketMakerAnalyzer()

    # Test with sample stock
    test_symbol = "VCB"
    analysis = analyzer.analyze_market_maker_style(test_symbol)

    print(f"📈 MARKET MAKER ANALYSIS: {test_symbol}")
    print("=" * 60)

    if 'error' not in analysis:
        print(f"Market Maker Style: {analysis['market_maker_style']['style_classification']}")
        print(f"Smart Money Flow: {analysis['smart_money_analysis']['flow_direction']}")
        print(f"Current Phase: {analysis['current_market_phase']['current_phase']}")
        print(f"Liquidity Grade: {analysis['liquidity_provision']['liquidity_grade']}")

        print(f"\n🎯 ACTIONABLE INSIGHTS:")
        print(f"Primary Opportunity: {analysis['actionable_insights']['primary_opportunity']}")

        print(f"\n📊 ENTRY SIGNALS:")
        for signal in analysis['entry_exit_signals']['entry_signals']:
            print(f"• {signal['signal']}: {signal['trigger']} ({signal['strength']})")

        # Save analysis
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/workspaces/BMAD-METHOD/session_logs/mm_analysis_{test_symbol}_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)

        print(f"\n💾 Analysis saved to: {filename}")
    else:
        print(f"❌ Error: {analysis['error']}")

    print("🚀 Market Maker Analysis System ready!")