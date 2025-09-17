#!/usr/bin/env python3
"""
Smart Money Signal System - Adapted for Vietnam Stock Analysis Dashboard
Advanced institutional behavior tracking integrated with existing database
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
from shared.models.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SmartMoneyAnalyzer:
    """Smart Money Analysis adapted for Vietnamese market and current database"""

    def __init__(self):
        self.db = get_db()

        # Vietnamese market-optimized configurations (enhanced sensitivity)
        self.config = {
            'volume_threshold_multiplier': 1.4,    # Reduced for more sensitivity
            'price_impact_threshold': 0.015,       # More sensitive to price changes
            'accumulation_period': 20,             # Shorter period for faster detection
            'momentum_period': 10,                 # More responsive momentum
            'trend_confirmation_days': 5,          # Faster trend confirmation
            'vietnamese_adjustments': {
                'banking_sector_weight': 1.25,     # Higher weight for banking leadership
                'foreign_ownership_factor': 1.3,   # Enhanced foreign interest factor
                'state_owned_factor': 0.85,        # Lower volatility for SOEs
                'volatility_adjustment': 1.5       # Account for VN market volatility
            }
        }

        # Signal weights
        self.weights = {
            'volume_signals': 0.25,
            'price_action': 0.25,
            'momentum': 0.20,
            'accumulation': 0.15,
            'smart_money_flow': 0.15
        }

        # Thresholds (adjusted for Vietnamese market sensitivity)
        self.thresholds = {
            'strong_buy': 70,   # Lowered for more signals
            'buy': 58,          # More responsive buy signals
            'weak_buy': 52,     # Earlier weak buy detection
            'hold': 42,         # Narrower hold range
            'sell': 38,         # Earlier sell signals
            'strong_sell': 25   # More definitive sell threshold
        }

    def analyze_symbol(self, symbol: str, days_back: int = 60) -> Dict:
        """Generate comprehensive smart money analysis for a symbol"""
        logger.info(f"Analyzing smart money signals for {symbol}")

        try:
            # Get data from database
            data = self._load_symbol_data(symbol, days_back)
            if data.empty:
                return {'symbol': symbol, 'error': 'No data available'}

            # Calculate technical indicators
            data = self._calculate_indicators(data)

            # Generate signal components
            volume_signals = self._analyze_volume_patterns(data)
            price_action = self._analyze_price_action(data)
            momentum = self._analyze_momentum(data)
            accumulation = self._analyze_accumulation(data)
            smart_flow = self._detect_smart_money_flow(data)

            # Calculate composite score
            composite = self._calculate_composite_score(
                volume_signals, price_action, momentum, accumulation, smart_flow
            )

            # Generate actionable insights
            entry_exit = self._generate_entry_exit_signals(data, composite)
            risk_analysis = self._calculate_risk_metrics(data)
            market_context = self._apply_vietnamese_context(symbol, composite)

            return {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'composite_score': composite,
                'signal_components': {
                    'volume_signals': volume_signals,
                    'price_action': price_action,
                    'momentum': momentum,
                    'accumulation': accumulation,
                    'smart_money_flow': smart_flow
                },
                'entry_exit_signals': entry_exit,
                'risk_analysis': risk_analysis,
                'market_context': market_context,
                'actionable_insights': self._generate_insights(composite, entry_exit, risk_analysis)
            }

        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def _load_symbol_data(self, symbol: str, days_back: int) -> pd.DataFrame:
        """Load price data from database"""
        # Get all available data for the symbol (since our date field has issues)
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT * FROM price_data
                WHERE stock_symbol = ?
                ORDER BY date
            """, (symbol,))
            price_data = [dict(row) for row in cursor.fetchall()]

        if not price_data:
            return pd.DataFrame()

        df = pd.DataFrame(price_data)

        # Handle the date format issue - convert sequential numbers to actual dates
        if 'date' in df.columns:
            # Create proper date sequence
            base_date = datetime.now() - timedelta(days=len(df))
            df['date'] = [base_date + timedelta(days=i) for i in range(len(df))]

            # Take only the last 'days_back' records
            df = df.tail(min(days_back, len(df)))

        return df.sort_values('date').reset_index(drop=True)

    def _calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate technical indicators"""
        # Moving averages
        data['sma_10'] = data['close'].rolling(10).mean()
        data['sma_20'] = data['close'].rolling(20).mean()
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()

        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()

        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))

        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']

        # On Balance Volume
        data['obv'] = (data['volume'] * ((data['close'] > data['close'].shift()).astype(int) * 2 - 1)).cumsum()

        # Bollinger Bands
        data['bb_middle'] = data['close'].rolling(20).mean()
        bb_std = data['close'].rolling(20).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)

        return data

    def _analyze_volume_patterns(self, data: pd.DataFrame) -> Dict:
        """Analyze volume patterns for smart money activity"""
        score = 50
        signals = []

        recent = data.tail(20)
        if len(recent) < 5:
            return {'score': score, 'signals': signals, 'strength': 'Insufficient Data'}

        current_volume = recent['volume'].iloc[-1]
        avg_volume = recent['volume_sma'].iloc[-1] if not pd.isna(recent['volume_sma'].iloc[-1]) else recent['volume'].mean()

        # Volume spike with minimal price impact (enhanced for VN market)
        price_change = abs(recent['close'].pct_change().iloc[-1]) * 100
        volume_spike_factor = current_volume / avg_volume

        if volume_spike_factor > self.config['volume_threshold_multiplier']:
            if price_change < self.config['price_impact_threshold'] * 100:
                signals.append({
                    'type': 'stealth_accumulation',
                    'description': f'Large volume ({volume_spike_factor:.1f}x) with minimal price impact',
                    'strength': 'Strong',
                    'bullish': True
                })
                score += 25  # Increased reward
            else:
                # High volume with price movement
                signals.append({
                    'type': 'volume_momentum',
                    'description': f'High volume ({volume_spike_factor:.1f}x) with price movement',
                    'strength': 'Medium',
                    'bullish': price_change > 0
                })
                score += 15 if price_change > 0 else -10

        # OBV divergence analysis
        if len(recent) >= 10:
            obv_trend = recent['obv'].corr(pd.Series(range(len(recent))))
            price_trend = recent['close'].corr(pd.Series(range(len(recent))))

            if obv_trend > 0.3 and price_trend < 0:
                signals.append({
                    'type': 'bullish_divergence',
                    'description': 'OBV rising while price declining',
                    'strength': 'Strong',
                    'bullish': True
                })
                score += 25

        # Volume trend
        volume_trend = recent['volume'].corr(pd.Series(range(len(recent))))
        if volume_trend > 0.5:
            signals.append({
                'type': 'increasing_volume',
                'description': 'Consistent volume increase',
                'strength': 'Medium',
                'bullish': True
            })
            score += 15

        strength = self._classify_strength(score)
        return {'score': score, 'signals': signals, 'strength': strength}

    def _analyze_price_action(self, data: pd.DataFrame) -> Dict:
        """Analyze price action signals"""
        score = 50
        signals = []

        recent = data.tail(20)
        if len(recent) < 10:
            return {'score': score, 'signals': signals, 'strength': 'Insufficient Data'}

        current = recent.iloc[-1]

        # Moving average alignment
        if (current['close'] > current['sma_10'] and
            current['sma_10'] > current['sma_20'] and
            not pd.isna(current['sma_10']) and not pd.isna(current['sma_20'])):
            signals.append({
                'type': 'bullish_ma_alignment',
                'description': 'Bullish moving average alignment',
                'strength': 'Strong',
                'bullish': True
            })
            score += 20

        # MACD signal
        if (not pd.isna(current['macd']) and not pd.isna(current['macd_signal']) and
            len(recent) >= 2):
            prev = recent.iloc[-2]
            if (current['macd'] > current['macd_signal'] and
                prev['macd'] <= prev['macd_signal']):
                signals.append({
                    'type': 'macd_bullish_crossover',
                    'description': 'MACD bullish crossover',
                    'strength': 'Medium',
                    'bullish': True
                })
                score += 15

        # Breakout detection
        if self._detect_breakout(data):
            signals.append({
                'type': 'price_breakout',
                'description': 'Price breakout detected',
                'strength': 'Strong',
                'bullish': True
            })
            score += 25

        strength = self._classify_strength(score)
        return {'score': score, 'signals': signals, 'strength': strength}

    def _analyze_momentum(self, data: pd.DataFrame) -> Dict:
        """Analyze momentum indicators"""
        score = 50
        signals = []

        recent = data.tail(20)
        if len(recent) < 10:
            return {'score': score, 'signals': signals, 'strength': 'Insufficient Data'}

        current = recent.iloc[-1]

        # RSI analysis
        if not pd.isna(current['rsi']):
            rsi = current['rsi']
            if rsi < 30:
                signals.append({
                    'type': 'rsi_oversold',
                    'description': f'RSI oversold at {rsi:.1f}',
                    'strength': 'Medium',
                    'bullish': True
                })
                score += 15
            elif rsi > 70:
                signals.append({
                    'type': 'rsi_overbought',
                    'description': f'RSI overbought at {rsi:.1f}',
                    'strength': 'Medium',
                    'bullish': False
                })
                score -= 15

        # Price momentum (enhanced sensitivity for VN market)
        if len(recent) >= 10:
            price_momentum_10d = (current['close'] / recent['close'].iloc[-10] - 1) * 100
            price_momentum_5d = (current['close'] / recent['close'].iloc[-5] - 1) * 100

            # Strong momentum detection
            if price_momentum_10d > 3 and current['volume_ratio'] > 1.2:
                signals.append({
                    'type': 'strong_momentum',
                    'description': f'Strong momentum {price_momentum_10d:.1f}% (10d) with volume',
                    'strength': 'Strong',
                    'bullish': True
                })
                score += 20

            # Medium momentum detection
            elif price_momentum_5d > 2 and current['volume_ratio'] > 1.1:
                signals.append({
                    'type': 'medium_momentum',
                    'description': f'Medium momentum {price_momentum_5d:.1f}% (5d)',
                    'strength': 'Medium',
                    'bullish': True
                })
                score += 12

            # Negative momentum detection
            elif price_momentum_10d < -3:
                signals.append({
                    'type': 'negative_momentum',
                    'description': f'Negative momentum {price_momentum_10d:.1f}% (10d)',
                    'strength': 'Medium',
                    'bullish': False
                })
                score -= 15

        strength = self._classify_strength(score)
        return {'score': score, 'signals': signals, 'strength': strength}

    def _analyze_accumulation(self, data: pd.DataFrame) -> Dict:
        """Analyze accumulation/distribution patterns"""
        score = 50
        signals = []

        recent = data.tail(self.config['accumulation_period'])
        if len(recent) < 10:
            return {'score': score, 'signals': signals, 'strength': 'Insufficient Data'}

        # Volume on up vs down days
        up_days = recent[recent['close'] > recent['close'].shift()]
        down_days = recent[recent['close'] <= recent['close'].shift()]

        if not up_days.empty and not down_days.empty:
            avg_vol_up = up_days['volume'].mean()
            avg_vol_down = down_days['volume'].mean()

            if avg_vol_up > avg_vol_down * 1.2:
                signals.append({
                    'type': 'volume_accumulation',
                    'description': 'Higher volume on up days',
                    'strength': 'Medium',
                    'bullish': True
                })
                score += 15

        # Stealth accumulation detection
        large_volume_days = recent[recent['volume'] > recent['volume'].quantile(0.8)]
        if not large_volume_days.empty:
            stealth_volume = 0
            for _, day in large_volume_days.iterrows():
                price_change = abs((day['close'] - day['open']) / day['open'])
                if price_change < 0.02:  # Minimal price impact
                    stealth_volume += day['volume']

            if stealth_volume > recent['volume'].sum() * 0.3:
                signals.append({
                    'type': 'stealth_accumulation',
                    'description': 'Stealth accumulation detected',
                    'strength': 'Strong',
                    'bullish': True
                })
                score += 25

        strength = self._classify_strength(score)
        return {'score': score, 'signals': signals, 'strength': strength}

    def _detect_smart_money_flow(self, data: pd.DataFrame) -> Dict:
        """Detect smart money flow patterns"""
        score = 50
        patterns = []

        recent = data.tail(30)
        if len(recent) < 15:
            return {'score': score, 'patterns': patterns, 'flow_direction': 'Insufficient Data'}

        # Pattern 1: Buying on weakness
        weak_days = recent[recent['close'] < recent['close'].shift()]
        if not weak_days.empty:
            avg_vol_weak = weak_days['volume'].mean()
            avg_vol_all = recent['volume'].mean()

            if avg_vol_weak > avg_vol_all * 1.1:
                patterns.append({
                    'pattern': 'buying_on_weakness',
                    'description': 'Smart money buying on weakness',
                    'bullish': True
                })
                score += 15

        # Pattern 2: Volume clustering
        volume_clusters = self._analyze_volume_clustering(recent)
        if volume_clusters['institutional_probability'] > 0.6:
            patterns.append({
                'pattern': 'volume_clustering',
                'description': 'Institutional volume clustering',
                'bullish': volume_clusters['net_bullish']
            })
            score += 15 if volume_clusters['net_bullish'] else -10

        # Determine flow direction
        if score >= 70:
            flow_direction = 'Strong Inflow'
        elif score >= 60:
            flow_direction = 'Moderate Inflow'
        elif score <= 40:
            flow_direction = 'Outflow'
        else:
            flow_direction = 'Neutral'

        return {'score': score, 'patterns': patterns, 'flow_direction': flow_direction}

    def _calculate_composite_score(self, volume, price, momentum, accumulation, smart_flow) -> Dict:
        """Calculate weighted composite score"""
        weighted_score = (
            volume['score'] * self.weights['volume_signals'] +
            price['score'] * self.weights['price_action'] +
            momentum['score'] * self.weights['momentum'] +
            accumulation['score'] * self.weights['accumulation'] +
            smart_flow['score'] * self.weights['smart_money_flow']
        )

        # Signal classification
        if weighted_score >= self.thresholds['strong_buy']:
            signal_class = 'Strong Buy'
            action = 'Aggressive accumulation recommended'
        elif weighted_score >= self.thresholds['buy']:
            signal_class = 'Buy'
            action = 'Accumulate on weakness'
        elif weighted_score >= self.thresholds['weak_buy']:
            signal_class = 'Weak Buy'
            action = 'Small position consideration'
        elif weighted_score >= self.thresholds['hold']:
            signal_class = 'Hold'
            action = 'Maintain current position'
        elif weighted_score >= self.thresholds['sell']:
            signal_class = 'Sell'
            action = 'Consider reducing position'
        else:
            signal_class = 'Strong Sell'
            action = 'Exit position recommended'

        return {
            'composite_score': weighted_score,
            'signal_class': signal_class,
            'recommended_action': action,
            'component_scores': {
                'volume': volume['score'],
                'price_action': price['score'],
                'momentum': momentum['score'],
                'accumulation': accumulation['score'],
                'smart_money_flow': smart_flow['score']
            },
            'signal_strength': self._classify_strength(weighted_score)
        }

    def _generate_entry_exit_signals(self, data: pd.DataFrame, composite: Dict) -> Dict:
        """Generate specific entry/exit signals"""
        current_price = data['close'].iloc[-1]

        signals = {
            'entry_signals': [],
            'exit_signals': [],
            'stop_loss': None,
            'targets': [],
            'position_sizing': 'Medium'
        }

        # Entry signals based on composite score
        if composite['composite_score'] >= self.thresholds['buy']:
            # Support level entry
            recent_low = data['low'].tail(20).min()
            if current_price <= recent_low * 1.03:
                signals['entry_signals'].append({
                    'type': 'Support Bounce',
                    'level': recent_low,
                    'urgency': 'High'
                })

            # Breakout entry
            recent_high = data['high'].tail(50).max()
            if current_price >= recent_high * 0.98:
                signals['entry_signals'].append({
                    'type': 'Breakout',
                    'level': recent_high * 1.005,
                    'urgency': 'High'
                })

        # Stop loss and targets
        volatility = data['close'].pct_change().std() * current_price
        signals['stop_loss'] = current_price - (volatility * 2)
        signals['targets'] = [
            current_price + (volatility * 2),
            current_price + (volatility * 3),
            current_price + (volatility * 4)
        ]

        # Position sizing
        if composite['composite_score'] >= self.thresholds['strong_buy']:
            signals['position_sizing'] = 'Large (3-5% portfolio)'
        elif composite['composite_score'] >= self.thresholds['buy']:
            signals['position_sizing'] = 'Medium (2-3% portfolio)'
        else:
            signals['position_sizing'] = 'Small (1-2% portfolio)'

        return signals

    def _calculate_risk_metrics(self, data: pd.DataFrame) -> Dict:
        """Calculate risk metrics"""
        returns = data['close'].pct_change().dropna()

        return {
            'volatility': returns.std() * np.sqrt(252) * 100,
            'max_drawdown': self._calculate_max_drawdown(data),
            'var_95': returns.quantile(0.05) * 100,
            'risk_grade': 'Medium',  # Simplified for now
            'liquidity_score': min(100, data['volume'].mean() / 100000)
        }

    def _apply_vietnamese_context(self, symbol: str, composite: Dict) -> Dict:
        """Apply Vietnamese market context"""
        adjustment_factor = 1.0
        context_notes = []

        # Banking sector boost
        if symbol in ['VCB', 'BID', 'CTG', 'TCB', 'MBB']:
            adjustment_factor *= self.config['vietnamese_adjustments']['banking_sector_weight']
            context_notes.append("Banking sector leadership in Vietnamese market")

        # Foreign ownership attractiveness
        if symbol in ['VCB', 'FPT', 'VIC', 'VHM', 'HPG']:
            adjustment_factor *= self.config['vietnamese_adjustments']['foreign_ownership_factor']
            context_notes.append("High foreign ownership potential")

        adjusted_score = composite['composite_score'] * adjustment_factor

        return {
            'original_score': composite['composite_score'],
            'adjusted_score': adjusted_score,
            'adjustment_factor': adjustment_factor,
            'context_notes': context_notes,
            'market_factors': {
                'banking_sector': symbol in ['VCB', 'BID', 'CTG', 'TCB', 'MBB'],
                'foreign_attractive': symbol in ['VCB', 'FPT', 'VIC', 'VHM', 'HPG']
            }
        }

    def _generate_insights(self, composite: Dict, entry_exit: Dict, risk: Dict) -> Dict:
        """Generate actionable insights"""
        insights = {
            'key_points': [],
            'risks': [],
            'opportunities': [],
            'next_actions': []
        }

        score = composite['composite_score']

        # Key points
        insights['key_points'].append(f"Signal strength: {composite['signal_strength']}")
        insights['key_points'].append(f"Recommended action: {composite['recommended_action']}")

        # Opportunities
        if score >= self.thresholds['buy']:
            insights['opportunities'].append("Strong smart money signals detected")
            insights['next_actions'].append("Consider initiating or adding to position")

        # Risks
        if risk['volatility'] > 30:
            insights['risks'].append("High volatility - use appropriate position sizing")

        if len(entry_exit['entry_signals']) == 0:
            insights['next_actions'].append("Wait for better entry opportunity")

        return insights

    # Helper methods
    def _detect_breakout(self, data: pd.DataFrame) -> bool:
        """Simple breakout detection"""
        if len(data) < 20:
            return False

        recent_high = data['high'].tail(50).max()
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()

        return (current_price > recent_high * 1.01 and
                current_volume > avg_volume * 1.3)

    def _analyze_volume_clustering(self, data: pd.DataFrame) -> Dict:
        """Analyze volume clustering for institutional activity"""
        volume_threshold = data['volume'].quantile(0.8)
        high_vol_days = data[data['volume'] > volume_threshold]

        if len(high_vol_days) < 3:
            return {'institutional_probability': 0.3, 'net_bullish': False}

        # Check clustering
        clustering_score = 0
        net_price_impact = 0

        for i in range(len(high_vol_days) - 1):
            if high_vol_days.index[i+1] - high_vol_days.index[i] <= 3:
                clustering_score += 1

        for _, day in high_vol_days.iterrows():
            price_impact = (day['close'] - day['open']) / day['open']
            net_price_impact += price_impact

        institutional_prob = min(1.0, clustering_score / len(high_vol_days) + 0.3)

        return {
            'institutional_probability': institutional_prob,
            'net_bullish': net_price_impact > 0
        }

    def _calculate_max_drawdown(self, data: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        returns = data['close'].pct_change().fillna(0)
        cumulative = (1 + returns).cumprod()
        peak = cumulative.expanding().max()
        drawdown = (cumulative - peak) / peak
        return drawdown.min() * 100

    def _classify_strength(self, score: float) -> str:
        """Classify signal strength"""
        if score >= 80:
            return 'Very Strong'
        elif score >= 65:
            return 'Strong'
        elif score >= 55:
            return 'Moderate'
        elif score >= 40:
            return 'Weak'
        else:
            return 'Very Weak'

    def get_market_overview(self) -> Dict:
        """Get smart money overview for all available stocks"""
        stocks = self.db.get_all_stocks()
        overview = {
            'strong_signals': [],
            'weak_signals': [],
            'market_sentiment': 'Neutral',
            'top_picks': []
        }

        total_score = 0
        analyzed_count = 0

        for stock in stocks:
            try:
                analysis = self.analyze_symbol(stock['symbol'], days_back=30)
                if 'error' not in analysis:
                    score = analysis['composite_score']['composite_score']
                    total_score += score
                    analyzed_count += 1

                    if score >= self.thresholds['buy']:
                        overview['strong_signals'].append({
                            'symbol': stock['symbol'],
                            'name': stock['name'],
                            'score': score,
                            'signal': analysis['composite_score']['signal_class']
                        })
                    elif score <= self.thresholds['sell']:
                        overview['weak_signals'].append({
                            'symbol': stock['symbol'],
                            'name': stock['name'],
                            'score': score,
                            'signal': analysis['composite_score']['signal_class']
                        })

            except Exception as e:
                logger.warning(f"Failed to analyze {stock['symbol']}: {e}")

        if analyzed_count > 0:
            avg_score = total_score / analyzed_count
            if avg_score >= 60:
                overview['market_sentiment'] = 'Bullish'
            elif avg_score <= 40:
                overview['market_sentiment'] = 'Bearish'

            # Top picks
            overview['top_picks'] = sorted(
                overview['strong_signals'],
                key=lambda x: x['score'],
                reverse=True
            )[:3]

        return overview