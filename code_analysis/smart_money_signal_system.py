#!/usr/bin/env python3
"""
Smart Money Signal System for Vietnam Stocks
Advanced technical analysis with smart money tracking indicators
Provides precise entry/exit signals based on institutional behavior patterns
"""

import vnstock as vn
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import ta  # Technical Analysis library
import warnings
warnings.filterwarnings('ignore')

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SmartMoneySignalSystem:
    def __init__(self):
        self.vnstock_client = vn.Vnstock()

        # Smart money signal configurations
        self.signal_config = {
            'volume_threshold_multiplier': 1.5,    # Volume spike threshold
            'price_impact_threshold': 0.02,        # Maximum price impact for stealth trades
            'accumulation_period': 20,             # Days to look for accumulation
            'distribution_period': 15,             # Days to look for distribution
            'momentum_period': 10,                 # Days for momentum analysis
            'trend_confirmation_days': 5           # Days for trend confirmation
        }

        # Signal weights for composite scoring
        self.signal_weights = {
            'volume_signals': 0.25,
            'price_action_signals': 0.25,
            'momentum_signals': 0.20,
            'accumulation_signals': 0.15,
            'smart_money_flow': 0.15
        }

        # Entry/Exit signal thresholds
        self.thresholds = {
            'strong_buy': 80,
            'buy': 65,
            'hold': 45,
            'sell': 35,
            'strong_sell': 20
        }

    def generate_smart_money_signals(self, symbol: str) -> Dict:
        """Generate comprehensive smart money signals for trading decisions"""

        logging.info(f"Generating smart money signals for {symbol}")

        try:
            # Get comprehensive data
            end_date = datetime.now()
            start_date = end_date - timedelta(days=200)  # Extended period for signal analysis

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'error': 'No data available'}

            # Calculate all technical indicators
            data = self.calculate_technical_indicators(data)

            # Generate signal components
            volume_signals = self.generate_volume_signals(data)
            price_action_signals = self.generate_price_action_signals(data)
            momentum_signals = self.generate_momentum_signals(data)
            accumulation_signals = self.generate_accumulation_signals(data)
            smart_money_flow = self.detect_smart_money_flow_patterns(data)

            # Calculate composite signal score
            composite_score = self.calculate_composite_signal_score(
                volume_signals, price_action_signals, momentum_signals,
                accumulation_signals, smart_money_flow
            )

            # Generate specific entry/exit signals
            entry_exit_signals = self.generate_entry_exit_signals(data, composite_score)

            # Risk management parameters
            risk_management = self.calculate_risk_parameters(data)

            # Market timing analysis
            market_timing = self.analyze_market_timing(data)

            return {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'composite_signal_score': composite_score,
                'signal_components': {
                    'volume_signals': volume_signals,
                    'price_action_signals': price_action_signals,
                    'momentum_signals': momentum_signals,
                    'accumulation_signals': accumulation_signals,
                    'smart_money_flow': smart_money_flow
                },
                'entry_exit_signals': entry_exit_signals,
                'risk_management': risk_management,
                'market_timing': market_timing,
                'actionable_recommendations': self.generate_actionable_recommendations(
                    composite_score, entry_exit_signals, risk_management
                ),
                'monitoring_alerts': self.setup_monitoring_alerts(data, composite_score)
            }

        except Exception as e:
            logging.error(f"Error generating smart money signals for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def calculate_technical_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive technical indicators"""

        # Price-based indicators
        data['sma_10'] = data['close'].rolling(10).mean()
        data['sma_20'] = data['close'].rolling(20).mean()
        data['sma_50'] = data['close'].rolling(50).mean()
        data['ema_12'] = data['close'].ewm(span=12).mean()
        data['ema_26'] = data['close'].ewm(span=26).mean()

        # MACD
        data['macd'] = data['ema_12'] - data['ema_26']
        data['macd_signal'] = data['macd'].ewm(span=9).mean()
        data['macd_histogram'] = data['macd'] - data['macd_signal']

        # RSI
        delta = data['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        data['rsi'] = 100 - (100 / (1 + rs))

        # Bollinger Bands
        bb_period = 20
        data['bb_middle'] = data['close'].rolling(bb_period).mean()
        bb_std = data['close'].rolling(bb_period).std()
        data['bb_upper'] = data['bb_middle'] + (bb_std * 2)
        data['bb_lower'] = data['bb_middle'] - (bb_std * 2)
        data['bb_width'] = (data['bb_upper'] - data['bb_lower']) / data['bb_middle']
        data['bb_position'] = (data['close'] - data['bb_lower']) / (data['bb_upper'] - data['bb_lower'])

        # Volume indicators
        data['volume_sma'] = data['volume'].rolling(20).mean()
        data['volume_ratio'] = data['volume'] / data['volume_sma']

        # On Balance Volume
        data['obv'] = (data['volume'] * ((data['close'] > data['close'].shift()).astype(int) * 2 - 1)).cumsum()

        # Average True Range
        data['high_low'] = data['high'] - data['low']
        data['high_close'] = abs(data['high'] - data['close'].shift())
        data['low_close'] = abs(data['low'] - data['close'].shift())
        data['atr'] = data[['high_low', 'high_close', 'low_close']].max(axis=1).rolling(14).mean()

        # Money Flow Index
        data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3
        data['money_flow'] = data['typical_price'] * data['volume']
        data['positive_flow'] = data['money_flow'].where(data['close'] > data['close'].shift(), 0).rolling(14).sum()
        data['negative_flow'] = data['money_flow'].where(data['close'] <= data['close'].shift(), 0).rolling(14).sum()
        data['mfi'] = 100 - (100 / (1 + data['positive_flow'] / data['negative_flow']))

        # Accumulation/Distribution Line
        data['ad_multiplier'] = ((data['close'] - data['low']) - (data['high'] - data['close'])) / (data['high'] - data['low'])
        data['ad_multiplier'] = data['ad_multiplier'].fillna(0)
        data['ad_volume'] = data['ad_multiplier'] * data['volume']
        data['ad_line'] = data['ad_volume'].cumsum()

        return data

    def generate_volume_signals(self, data: pd.DataFrame) -> Dict:
        """Generate volume-based smart money signals"""

        volume_signals = {
            'score': 50,
            'signals': [],
            'strength': 'Neutral'
        }

        # Volume spike analysis
        recent_data = data.tail(20)
        avg_volume = recent_data['volume_sma'].iloc[-1]
        current_volume = recent_data['volume'].iloc[-1]

        # Large volume with minimal price impact (smart money)
        price_impact = abs(recent_data['close'].pct_change().iloc[-1]) * 100
        volume_spike = current_volume > avg_volume * self.signal_config['volume_threshold_multiplier']

        if volume_spike and price_impact < self.signal_config['price_impact_threshold'] * 100:
            volume_signals['signals'].append({
                'type': 'stealth_accumulation',
                'description': 'Large volume with minimal price impact',
                'bullish': True,
                'strength': 'Strong'
            })
            volume_signals['score'] += 20

        # Volume trend analysis
        volume_trend = recent_data['volume'].corr(pd.Series(range(len(recent_data))))
        if volume_trend > 0.5:
            volume_signals['signals'].append({
                'type': 'increasing_volume',
                'description': 'Consistent volume increase',
                'bullish': True,
                'strength': 'Medium'
            })
            volume_signals['score'] += 15

        # On Balance Volume divergence
        obv_trend = recent_data['obv'].corr(pd.Series(range(len(recent_data))))
        price_trend = recent_data['close'].corr(pd.Series(range(len(recent_data))))

        if obv_trend > 0.3 and price_trend < 0:
            volume_signals['signals'].append({
                'type': 'bullish_divergence',
                'description': 'OBV rising while price declining',
                'bullish': True,
                'strength': 'Strong'
            })
            volume_signals['score'] += 25

        # Volume confirmation
        price_change = (recent_data['close'].iloc[-1] / recent_data['close'].iloc[-5]) - 1
        if price_change > 0.02 and recent_data['volume_ratio'].iloc[-1] > 1.3:
            volume_signals['signals'].append({
                'type': 'volume_confirmation',
                'description': 'Price breakout with volume confirmation',
                'bullish': True,
                'strength': 'Medium'
            })
            volume_signals['score'] += 15

        # Determine overall strength
        if volume_signals['score'] >= 80:
            volume_signals['strength'] = 'Very Strong'
        elif volume_signals['score'] >= 65:
            volume_signals['strength'] = 'Strong'
        elif volume_signals['score'] >= 55:
            volume_signals['strength'] = 'Moderate'
        elif volume_signals['score'] <= 35:
            volume_signals['strength'] = 'Weak'

        return volume_signals

    def generate_price_action_signals(self, data: pd.DataFrame) -> Dict:
        """Generate price action signals"""

        price_signals = {
            'score': 50,
            'signals': [],
            'strength': 'Neutral'
        }

        recent_data = data.tail(20)
        current = recent_data.iloc[-1]

        # Moving average signals
        if current['close'] > current['sma_10'] > current['sma_20'] > current['sma_50']:
            price_signals['signals'].append({
                'type': 'bullish_ma_alignment',
                'description': 'Bullish moving average alignment',
                'bullish': True,
                'strength': 'Strong'
            })
            price_signals['score'] += 20

        # Bollinger Band signals
        if current['bb_position'] < 0.2:  # Near lower band
            price_signals['signals'].append({
                'type': 'oversold_bb',
                'description': 'Price near Bollinger Band lower band',
                'bullish': True,
                'strength': 'Medium'
            })
            price_signals['score'] += 15

        elif current['bb_position'] > 0.8:  # Near upper band
            price_signals['signals'].append({
                'type': 'overbought_bb',
                'description': 'Price near Bollinger Band upper band',
                'bullish': False,
                'strength': 'Medium'
            })
            price_signals['score'] -= 15

        # MACD signals
        if current['macd'] > current['macd_signal'] and recent_data['macd'].iloc[-2] <= recent_data['macd_signal'].iloc[-2]:
            price_signals['signals'].append({
                'type': 'macd_bullish_crossover',
                'description': 'MACD bullish crossover',
                'bullish': True,
                'strength': 'Medium'
            })
            price_signals['score'] += 15

        # Support/Resistance levels
        support_resistance = self.identify_support_resistance_levels(data)
        current_price = current['close']

        for level in support_resistance['support_levels']:
            if abs(current_price - level) / level < 0.02:  # Within 2% of support
                price_signals['signals'].append({
                    'type': 'support_test',
                    'description': f'Price testing support at {level:.2f}',
                    'bullish': True,
                    'strength': 'Medium'
                })
                price_signals['score'] += 12

        # Breakout signals
        if self.detect_breakout(data):
            price_signals['signals'].append({
                'type': 'breakout',
                'description': 'Price breakout detected',
                'bullish': True,
                'strength': 'Strong'
            })
            price_signals['score'] += 25

        # Determine strength
        if price_signals['score'] >= 80:
            price_signals['strength'] = 'Very Strong'
        elif price_signals['score'] >= 65:
            price_signals['strength'] = 'Strong'
        elif price_signals['score'] >= 55:
            price_signals['strength'] = 'Moderate'
        elif price_signals['score'] <= 35:
            price_signals['strength'] = 'Weak'

        return price_signals

    def generate_momentum_signals(self, data: pd.DataFrame) -> Dict:
        """Generate momentum-based signals"""

        momentum_signals = {
            'score': 50,
            'signals': [],
            'strength': 'Neutral'
        }

        recent_data = data.tail(20)
        current = recent_data.iloc[-1]

        # RSI analysis
        current_rsi = current['rsi']
        if current_rsi < 30:
            momentum_signals['signals'].append({
                'type': 'rsi_oversold',
                'description': f'RSI oversold at {current_rsi:.1f}',
                'bullish': True,
                'strength': 'Medium'
            })
            momentum_signals['score'] += 15
        elif current_rsi > 70:
            momentum_signals['signals'].append({
                'type': 'rsi_overbought',
                'description': f'RSI overbought at {current_rsi:.1f}',
                'bullish': False,
                'strength': 'Medium'
            })
            momentum_signals['score'] -= 15

        # RSI divergence
        rsi_trend = recent_data['rsi'].corr(pd.Series(range(len(recent_data))))
        price_trend = recent_data['close'].corr(pd.Series(range(len(recent_data))))

        if rsi_trend > 0.3 and price_trend < -0.1:
            momentum_signals['signals'].append({
                'type': 'bullish_rsi_divergence',
                'description': 'RSI showing bullish divergence',
                'bullish': True,
                'strength': 'Strong'
            })
            momentum_signals['score'] += 20

        # Money Flow Index
        current_mfi = current['mfi']
        if current_mfi < 20:
            momentum_signals['signals'].append({
                'type': 'mfi_oversold',
                'description': f'Money Flow Index oversold at {current_mfi:.1f}',
                'bullish': True,
                'strength': 'Medium'
            })
            momentum_signals['score'] += 12

        # Momentum persistence
        price_momentum = (current['close'] / recent_data['close'].iloc[-10] - 1) * 100
        if price_momentum > 5 and recent_data['volume_ratio'].iloc[-1] > 1.2:
            momentum_signals['signals'].append({
                'type': 'strong_momentum',
                'description': f'Strong price momentum {price_momentum:.1f}% with volume',
                'bullish': True,
                'strength': 'Strong'
            })
            momentum_signals['score'] += 18

        # Determine strength
        if momentum_signals['score'] >= 80:
            momentum_signals['strength'] = 'Very Strong'
        elif momentum_signals['score'] >= 65:
            momentum_signals['strength'] = 'Strong'
        elif momentum_signals['score'] >= 55:
            momentum_signals['strength'] = 'Moderate'
        elif momentum_signals['score'] <= 35:
            momentum_signals['strength'] = 'Weak'

        return momentum_signals

    def generate_accumulation_signals(self, data: pd.DataFrame) -> Dict:
        """Generate accumulation/distribution signals"""

        accumulation_signals = {
            'score': 50,
            'signals': [],
            'strength': 'Neutral'
        }

        recent_data = data.tail(self.signal_config['accumulation_period'])

        # Accumulation/Distribution Line trend
        ad_trend = recent_data['ad_line'].corr(pd.Series(range(len(recent_data))))
        if ad_trend > 0.5:
            accumulation_signals['signals'].append({
                'type': 'ad_line_accumulation',
                'description': 'Accumulation/Distribution Line showing accumulation',
                'bullish': True,
                'strength': 'Medium'
            })
            accumulation_signals['score'] += 15

        # Volume pattern analysis
        up_days = recent_data[recent_data['close'] > recent_data['close'].shift()]
        down_days = recent_data[recent_data['close'] <= recent_data['close'].shift()]

        if not up_days.empty and not down_days.empty:
            avg_volume_up = up_days['volume'].mean()
            avg_volume_down = down_days['volume'].mean()

            if avg_volume_up > avg_volume_down * 1.2:
                accumulation_signals['signals'].append({
                    'type': 'volume_accumulation',
                    'description': 'Higher volume on up days indicates accumulation',
                    'bullish': True,
                    'strength': 'Medium'
                })
                accumulation_signals['score'] += 15

        # Smart money accumulation pattern
        large_volume_days = recent_data[recent_data['volume'] > recent_data['volume_sma']]
        if not large_volume_days.empty:
            net_accumulation = 0
            for _, day in large_volume_days.iterrows():
                price_change = (day['close'] - day['open']) / day['open']
                if abs(price_change) < 0.02:  # Minimal price impact
                    net_accumulation += day['volume']

            if net_accumulation > recent_data['volume'].sum() * 0.3:
                accumulation_signals['signals'].append({
                    'type': 'stealth_accumulation',
                    'description': 'Stealth accumulation by smart money detected',
                    'bullish': True,
                    'strength': 'Strong'
                })
                accumulation_signals['score'] += 25

        # Determine strength
        if accumulation_signals['score'] >= 75:
            accumulation_signals['strength'] = 'Very Strong'
        elif accumulation_signals['score'] >= 65:
            accumulation_signals['strength'] = 'Strong'
        elif accumulation_signals['score'] >= 55:
            accumulation_signals['strength'] = 'Moderate'
        elif accumulation_signals['score'] <= 40:
            accumulation_signals['strength'] = 'Weak'

        return accumulation_signals

    def detect_smart_money_flow_patterns(self, data: pd.DataFrame) -> Dict:
        """Detect sophisticated smart money flow patterns"""

        smart_money_flow = {
            'score': 50,
            'flow_direction': 'Neutral',
            'patterns': [],
            'confidence': 'Medium'
        }

        recent_data = data.tail(30)

        # Pattern 1: Consistent accumulation on weakness
        weak_days = recent_data[recent_data['close'] < recent_data['close'].shift()]
        if not weak_days.empty:
            avg_volume_weak_days = weak_days['volume'].mean()
            avg_volume_all = recent_data['volume'].mean()

            if avg_volume_weak_days > avg_volume_all * 1.1:
                smart_money_flow['patterns'].append({
                    'pattern': 'buying_on_weakness',
                    'description': 'Smart money buying on weakness',
                    'bullish': True
                })
                smart_money_flow['score'] += 15

        # Pattern 2: Time-based institutional patterns
        morning_hours = recent_data.head(len(recent_data)//2)  # Proxy for morning trading
        afternoon_hours = recent_data.tail(len(recent_data)//2)

        morning_volume = morning_hours['volume'].mean()
        afternoon_volume = afternoon_hours['volume'].mean()

        if morning_volume > afternoon_volume * 1.3:
            smart_money_flow['patterns'].append({
                'pattern': 'institutional_timing',
                'description': 'Institutional trading patterns detected',
                'bullish': True
            })
            smart_money_flow['score'] += 12

        # Pattern 3: Price efficiency (minimal gaps and smooth moves)
        price_efficiency = self.calculate_price_efficiency(recent_data)
        if price_efficiency > 0.7:
            smart_money_flow['patterns'].append({
                'pattern': 'price_efficiency',
                'description': 'Efficient price discovery indicates institutional presence',
                'bullish': True
            })
            smart_money_flow['score'] += 10

        # Pattern 4: Volume clustering analysis
        volume_clusters = self.analyze_volume_clustering(recent_data)
        if volume_clusters['institutional_probability'] > 0.6:
            smart_money_flow['patterns'].append({
                'pattern': 'volume_clustering',
                'description': 'Institutional volume clustering detected',
                'bullish': volume_clusters['net_bullish']
            })
            smart_money_flow['score'] += 15 if volume_clusters['net_bullish'] else -10

        # Determine flow direction and confidence
        if smart_money_flow['score'] >= 70:
            smart_money_flow['flow_direction'] = 'Strong Inflow'
            smart_money_flow['confidence'] = 'High'
        elif smart_money_flow['score'] >= 60:
            smart_money_flow['flow_direction'] = 'Moderate Inflow'
            smart_money_flow['confidence'] = 'Medium-High'
        elif smart_money_flow['score'] <= 30:
            smart_money_flow['flow_direction'] = 'Outflow'
            smart_money_flow['confidence'] = 'Medium'
        elif smart_money_flow['score'] <= 40:
            smart_money_flow['flow_direction'] = 'Weak Outflow'
            smart_money_flow['confidence'] = 'Medium'

        return smart_money_flow

    def calculate_composite_signal_score(self, volume_signals: Dict, price_signals: Dict,
                                       momentum_signals: Dict, accumulation_signals: Dict,
                                       smart_money_flow: Dict) -> Dict:
        """Calculate weighted composite signal score"""

        weighted_score = (
            volume_signals['score'] * self.signal_weights['volume_signals'] +
            price_signals['score'] * self.signal_weights['price_action_signals'] +
            momentum_signals['score'] * self.signal_weights['momentum_signals'] +
            accumulation_signals['score'] * self.signal_weights['accumulation_signals'] +
            smart_money_flow['score'] * self.signal_weights['smart_money_flow']
        )

        # Determine signal classification
        if weighted_score >= self.thresholds['strong_buy']:
            signal_class = 'Strong Buy Signal'
            action = 'Aggressive accumulation recommended'
        elif weighted_score >= self.thresholds['buy']:
            signal_class = 'Buy Signal'
            action = 'Accumulate on weakness'
        elif weighted_score >= self.thresholds['hold']:
            signal_class = 'Hold Signal'
            action = 'Maintain current position'
        elif weighted_score >= self.thresholds['sell']:
            signal_class = 'Sell Signal'
            action = 'Consider reducing position'
        else:
            signal_class = 'Strong Sell Signal'
            action = 'Exit position recommended'

        return {
            'composite_score': weighted_score,
            'signal_classification': signal_class,
            'recommended_action': action,
            'component_scores': {
                'volume': volume_signals['score'],
                'price_action': price_signals['score'],
                'momentum': momentum_signals['score'],
                'accumulation': accumulation_signals['score'],
                'smart_money_flow': smart_money_flow['score']
            },
            'signal_strength': self.classify_signal_strength(weighted_score)
        }

    def generate_entry_exit_signals(self, data: pd.DataFrame, composite_score: Dict) -> Dict:
        """Generate specific entry and exit signals with precise levels"""

        signals = {
            'entry_signals': [],
            'exit_signals': [],
            'stop_loss_levels': {},
            'target_levels': {},
            'risk_reward_ratio': None,
            'position_sizing_recommendation': {}
        }

        current_price = data['close'].iloc[-1]
        atr = data['atr'].iloc[-1]

        # Entry signals based on composite score
        if composite_score['composite_score'] >= self.thresholds['buy']:

            # Support level entry
            support_levels = self.identify_support_resistance_levels(data)['support_levels']
            if support_levels:
                nearest_support = min(support_levels, key=lambda x: abs(x - current_price))
                if current_price <= nearest_support * 1.02:
                    signals['entry_signals'].append({
                        'type': 'support_bounce',
                        'entry_price': nearest_support,
                        'reasoning': 'Entry on support level bounce',
                        'urgency': 'High' if current_price <= nearest_support * 1.01 else 'Medium'
                    })

            # Breakout entry
            resistance_levels = self.identify_support_resistance_levels(data)['resistance_levels']
            if resistance_levels:
                nearest_resistance = min(resistance_levels, key=lambda x: abs(x - current_price))
                if current_price >= nearest_resistance * 0.98:
                    signals['entry_signals'].append({
                        'type': 'breakout',
                        'entry_price': nearest_resistance * 1.005,  # Slightly above resistance
                        'reasoning': 'Breakout entry above resistance',
                        'urgency': 'High'
                    })

            # Pullback entry (for strong signals)
            if composite_score['composite_score'] >= self.thresholds['strong_buy']:
                pullback_level = current_price * 0.97  # 3% pullback
                signals['entry_signals'].append({
                    'type': 'pullback',
                    'entry_price': pullback_level,
                    'reasoning': 'Entry on minor pullback in strong uptrend',
                    'urgency': 'Medium'
                })

        # Stop loss levels
        signals['stop_loss_levels'] = {
            'conservative': current_price - (atr * 2),
            'moderate': current_price - (atr * 1.5),
            'aggressive': current_price - (atr * 1)
        }

        # Target levels
        signals['target_levels'] = {
            'target_1': current_price + (atr * 2),    # 2:1 reward:risk
            'target_2': current_price + (atr * 3),    # 3:1 reward:risk
            'target_3': current_price + (atr * 4.5)   # 4.5:1 reward:risk
        }

        # Exit signals
        if composite_score['composite_score'] <= self.thresholds['sell']:
            signals['exit_signals'].append({
                'type': 'signal_deterioration',
                'reasoning': 'Composite signals turned negative',
                'urgency': 'High' if composite_score['composite_score'] <= self.thresholds['strong_sell'] else 'Medium'
            })

        # Position sizing recommendation
        signal_strength = composite_score['composite_score']
        if signal_strength >= self.thresholds['strong_buy']:
            position_size = 'Large (3-5% of portfolio)'
        elif signal_strength >= self.thresholds['buy']:
            position_size = 'Medium (2-3% of portfolio)'
        else:
            position_size = 'Small (1-2% of portfolio)'

        signals['position_sizing_recommendation'] = {
            'recommended_size': position_size,
            'risk_per_trade': '1-2% of portfolio',
            'max_correlation_exposure': '10% in same sector'
        }

        # Risk-reward calculation
        if signals['entry_signals'] and signals['stop_loss_levels'] and signals['target_levels']:
            avg_entry = sum(signal['entry_price'] for signal in signals['entry_signals']) / len(signals['entry_signals'])
            stop_loss = signals['stop_loss_levels']['moderate']
            target = signals['target_levels']['target_2']

            risk = avg_entry - stop_loss
            reward = target - avg_entry
            signals['risk_reward_ratio'] = reward / risk if risk > 0 else None

        return signals

    def calculate_risk_parameters(self, data: pd.DataFrame) -> Dict:
        """Calculate comprehensive risk parameters"""

        risk_params = {
            'volatility_metrics': {},
            'liquidity_risk': {},
            'market_risk': {},
            'position_risk': {},
            'overall_risk_score': 50
        }

        # Volatility metrics
        returns = data['close'].pct_change().dropna()
        risk_params['volatility_metrics'] = {
            'daily_volatility': returns.std() * 100,
            'annualized_volatility': returns.std() * np.sqrt(252) * 100,
            'downside_volatility': returns[returns < 0].std() * np.sqrt(252) * 100,
            'maximum_drawdown': self.calculate_maximum_drawdown(data),
            'var_95': returns.quantile(0.05) * 100  # Value at Risk 95%
        }

        # Liquidity risk
        avg_volume = data['volume'].tail(20).mean()
        volume_consistency = 1 / (data['volume'].tail(20).std() / avg_volume + 0.01)

        risk_params['liquidity_risk'] = {
            'average_volume': avg_volume,
            'volume_consistency': volume_consistency,
            'liquidity_score': min(100, volume_consistency * 50 + (avg_volume / 1000000) * 10),
            'risk_level': 'Low' if avg_volume > 500000 and volume_consistency > 0.7 else 'Medium'
        }

        # Overall risk score calculation
        volatility_risk = min(30, risk_params['volatility_metrics']['annualized_volatility'])
        liquidity_risk = 100 - risk_params['liquidity_risk']['liquidity_score']

        risk_params['overall_risk_score'] = (volatility_risk + liquidity_risk) / 2
        risk_params['risk_grade'] = self.grade_risk(risk_params['overall_risk_score'])

        return risk_params

    def analyze_market_timing(self, data: pd.DataFrame) -> Dict:
        """Analyze optimal market timing"""

        timing_analysis = {
            'current_market_phase': '',
            'optimal_entry_timing': '',
            'seasonal_factors': {},
            'momentum_timing': {},
            'volume_timing': {}
        }

        recent_data = data.tail(30)

        # Market phase identification
        price_trend = recent_data['close'].corr(pd.Series(range(len(recent_data))))
        volume_trend = recent_data['volume'].corr(pd.Series(range(len(recent_data))))

        if price_trend > 0.3 and volume_trend > 0.2:
            timing_analysis['current_market_phase'] = 'Accumulation Phase'
            timing_analysis['optimal_entry_timing'] = 'Favorable - Early stage opportunity'
        elif price_trend > 0.5 and volume_trend > 0.4:
            timing_analysis['current_market_phase'] = 'Markup Phase'
            timing_analysis['optimal_entry_timing'] = 'Good - Momentum building'
        elif price_trend < -0.3:
            timing_analysis['current_market_phase'] = 'Distribution Phase'
            timing_analysis['optimal_entry_timing'] = 'Poor - Wait for reversal signals'
        else:
            timing_analysis['current_market_phase'] = 'Consolidation Phase'
            timing_analysis['optimal_entry_timing'] = 'Neutral - Wait for breakout'

        # Momentum timing
        rsi = data['rsi'].iloc[-1]
        timing_analysis['momentum_timing'] = {
            'rsi_level': rsi,
            'timing_assessment': 'Oversold - Good timing' if rsi < 35 else 'Overbought - Poor timing' if rsi > 65 else 'Neutral timing'
        }

        return timing_analysis

    # Helper methods

    def identify_support_resistance_levels(self, data: pd.DataFrame) -> Dict:
        """Identify key support and resistance levels"""

        # Simple pivot point method
        window = 20
        highs = data['high'].rolling(window=window, center=True).max()
        lows = data['low'].rolling(window=window, center=True).min()

        resistance_levels = data[data['high'] == highs]['high'].dropna().unique()
        support_levels = data[data['low'] == lows]['low'].dropna().unique()

        # Keep only recent and significant levels
        current_price = data['close'].iloc[-1]
        resistance_levels = [r for r in resistance_levels if current_price * 0.9 < r < current_price * 1.2]
        support_levels = [s for s in support_levels if current_price * 0.8 < s < current_price * 1.1]

        return {
            'resistance_levels': sorted(resistance_levels, reverse=True)[:3],
            'support_levels': sorted(support_levels, reverse=True)[:3]
        }

    def detect_breakout(self, data: pd.DataFrame) -> bool:
        """Detect if stock is breaking out"""
        recent_data = data.tail(10)

        # Check if current price is above recent resistance with volume
        recent_high = data.tail(50)['high'].max()
        current_price = data['close'].iloc[-1]
        current_volume = data['volume'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()

        return (current_price > recent_high * 1.01 and
                current_volume > avg_volume * 1.3)

    def calculate_price_efficiency(self, data: pd.DataFrame) -> float:
        """Calculate price discovery efficiency"""
        returns = data['close'].pct_change().dropna()

        # Measure of return smoothness (less erratic = more efficient)
        return_smoothness = 1 / (returns.std() + 0.01)

        # Measure of gap frequency (fewer gaps = more efficient)
        gaps = abs((data['open'] - data['close'].shift()) / data['close'].shift()).dropna()
        gap_frequency = 1 / (gaps.mean() + 0.01)

        return min(1.0, (return_smoothness * 0.1 + gap_frequency * 0.1) / 2)

    def analyze_volume_clustering(self, data: pd.DataFrame) -> Dict:
        """Analyze volume clustering patterns"""

        # Identify volume clusters (institutional block trading)
        volume_threshold = data['volume'].quantile(0.8)
        high_volume_days = data[data['volume'] > volume_threshold]

        if len(high_volume_days) < 3:
            return {'institutional_probability': 0.3, 'net_bullish': False}

        # Check for clustering (multiple high-volume days close together)
        clustering_score = 0
        net_price_impact = 0

        for i in range(len(high_volume_days) - 1):
            # Handle both datetime and integer index types
            index_diff = high_volume_days.index[i+1] - high_volume_days.index[i]
            if hasattr(index_diff, 'days'):
                # Datetime index - use .days
                if index_diff.days <= 3:
                    clustering_score += 1
            else:
                # Integer index - treat as sequential days
                if index_diff <= 3:
                    clustering_score += 1

        # Net price impact
        for _, day in high_volume_days.iterrows():
            price_impact = (day['close'] - day['open']) / day['open']
            net_price_impact += price_impact

        institutional_probability = min(1.0, clustering_score / len(high_volume_days) + 0.3)

        return {
            'institutional_probability': institutional_probability,
            'net_bullish': net_price_impact > 0,
            'clustering_score': clustering_score
        }

    def calculate_maximum_drawdown(self, data: pd.DataFrame) -> float:
        """Calculate maximum drawdown"""
        cumulative_returns = (1 + data['close'].pct_change()).cumprod()
        peak = cumulative_returns.expanding().max()
        drawdown = (cumulative_returns - peak) / peak
        return drawdown.min() * 100

    def classify_signal_strength(self, score: float) -> str:
        """Classify signal strength"""
        if score >= 85:
            return 'Very Strong'
        elif score >= 70:
            return 'Strong'
        elif score >= 55:
            return 'Moderate'
        elif score >= 40:
            return 'Weak'
        else:
            return 'Very Weak'

    def grade_risk(self, risk_score: float) -> str:
        """Grade overall risk level"""
        if risk_score <= 20:
            return 'A - Low Risk'
        elif risk_score <= 35:
            return 'B - Moderate Risk'
        elif risk_score <= 50:
            return 'C - Medium Risk'
        elif risk_score <= 65:
            return 'D - High Risk'
        else:
            return 'F - Very High Risk'

    def generate_actionable_recommendations(self, composite_score: Dict, entry_exit: Dict, risk: Dict) -> Dict:
        """Generate actionable trading recommendations"""

        recommendations = {
            'immediate_actions': [],
            'monitoring_actions': [],
            'risk_management': [],
            'timing_recommendations': []
        }

        score = composite_score['composite_score']

        # Immediate actions
        if score >= self.thresholds['strong_buy']:
            recommendations['immediate_actions'].append("Initiate position immediately - strong signals aligned")
            recommendations['immediate_actions'].append("Consider larger position size due to high conviction")
        elif score >= self.thresholds['buy']:
            recommendations['immediate_actions'].append("Begin accumulation on any weakness")
            recommendations['immediate_actions'].append("Scale into position over 3-5 days")
        elif score <= self.thresholds['sell']:
            recommendations['immediate_actions'].append("Consider reducing or exiting position")

        # Risk management
        recommendations['risk_management'].append(f"Set stop loss at {entry_exit['stop_loss_levels']['moderate']:.2f}")
        recommendations['risk_management'].append(f"Risk grade: {risk['risk_grade']}")
        if risk['overall_risk_score'] > 60:
            recommendations['risk_management'].append("Reduce position size due to elevated risk")

        # Monitoring actions
        recommendations['monitoring_actions'].append("Monitor volume patterns for institutional activity")
        recommendations['monitoring_actions'].append("Watch for support/resistance level tests")

        return recommendations

    def setup_monitoring_alerts(self, data: pd.DataFrame, composite_score: Dict) -> Dict:
        """Setup monitoring alerts for key levels and signals"""

        alerts = {
            'price_alerts': [],
            'volume_alerts': [],
            'signal_alerts': [],
            'update_frequency': 'Daily'
        }

        current_price = data['close'].iloc[-1]
        avg_volume = data['volume'].tail(20).mean()

        # Price alerts
        support_resistance = self.identify_support_resistance_levels(data)

        for resistance in support_resistance['resistance_levels'][:2]:
            alerts['price_alerts'].append({
                'level': resistance,
                'type': 'resistance_test',
                'message': f"Price approaching resistance at {resistance:.2f}"
            })

        for support in support_resistance['support_levels'][:2]:
            alerts['price_alerts'].append({
                'level': support,
                'type': 'support_test',
                'message': f"Price approaching support at {support:.2f}"
            })

        # Volume alerts
        alerts['volume_alerts'].append({
            'threshold': avg_volume * 1.5,
            'type': 'volume_spike',
            'message': 'Unusual volume spike detected - check for news or institutional activity'
        })

        # Signal alerts
        if composite_score['composite_score'] > 70:
            alerts['signal_alerts'].append({
                'condition': 'signal_deterioration',
                'threshold': 65,
                'message': 'Strong signals weakening - consider profit taking'
            })

        return alerts

if __name__ == "__main__":
    signal_system = SmartMoneySignalSystem()

    # Test signal generation
    test_symbol = "VCB"
    signals = signal_system.generate_smart_money_signals(test_symbol)

    print(f"🎯 SMART MONEY SIGNALS: {test_symbol}")
    print("=" * 60)

    if 'error' not in signals:
        composite = signals['composite_signal_score']
        print(f"Composite Signal Score: {composite['composite_score']:.1f}")
        print(f"Signal Classification: {composite['signal_classification']}")
        print(f"Recommended Action: {composite['recommended_action']}")

        print(f"\n📊 SIGNAL COMPONENTS:")
        for component, score in composite['component_scores'].items():
            print(f"{component.replace('_', ' ').title()}: {score:.1f}")

        print(f"\n🎯 ENTRY SIGNALS:")
        for signal in signals['entry_exit_signals']['entry_signals']:
            print(f"• {signal['type']}: {signal['entry_price']:.2f} - {signal['reasoning']}")

        print(f"\n⚠️ RISK MANAGEMENT:")
        risk = signals['risk_management']
        print(f"Risk Grade: {risk['risk_grade']}")
        print(f"Position Sizing: {signals['entry_exit_signals']['position_sizing_recommendation']['recommended_size']}")

        # Save signals
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/workspaces/BMAD-METHOD/session_logs/smart_money_signals_{test_symbol}_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(signals, f, indent=2, default=str)

        print(f"\n💾 Signals saved to: {filename}")
    else:
        print(f"❌ Error: {signals['error']}")

    print("\n🚀 Smart Money Signal System Ready!")
    print("Features:")
    print("• Advanced volume analysis")
    print("• Price action recognition")
    print("• Momentum indicators")
    print("• Accumulation/distribution detection")
    print("• Smart money flow patterns")
    print("• Precise entry/exit levels")
    print("• Risk management parameters")
    print("• Market timing analysis")