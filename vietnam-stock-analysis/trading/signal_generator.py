#!/usr/bin/env python3
"""
Real-Time Trading Signal Generator
High-precision entry/exit signals for Vietnamese market trading
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.models.database import get_db
from shared.analysis.smart_money import SmartMoneyAnalyzer
from trading.risk_manager import VietnameseRiskManager

class VietnameseTradingSignals:
    """Advanced real-time trading signal generation for Vietnamese stocks"""

    def __init__(self):
        self.db = get_db()
        self.analyzer = SmartMoneyAnalyzer()
        self.risk_manager = VietnameseRiskManager()

        # Signal generation parameters
        self.signal_config = {
            'strong_buy_threshold': 75,        # Strong buy signal threshold
            'buy_threshold': 62,               # Buy signal threshold
            'weak_buy_threshold': 55,          # Weak buy threshold
            'hold_threshold_upper': 54,        # Upper hold range
            'hold_threshold_lower': 46,        # Lower hold range
            'weak_sell_threshold': 45,         # Weak sell threshold
            'sell_threshold': 38,              # Sell signal threshold
            'strong_sell_threshold': 25,       # Strong sell threshold
            'confirmation_period': 2,          # Days for signal confirmation
            'momentum_weight': 0.25,           # Momentum component weight
            'volume_weight': 0.20,             # Volume component weight
            'accumulation_weight': 0.30,       # Accumulation component weight
            'smart_flow_weight': 0.25          # Smart money flow weight
        }

        # Entry/exit precision parameters
        self.precision_config = {
            'intraday_precision': True,        # Use intraday precision
            'support_resistance_levels': 3,   # Number of S/R levels to identify
            'volatility_breakout_threshold': 1.5,  # ATR multiplier for breakouts
            'volume_surge_threshold': 2.0,    # Volume surge multiplier
            'price_momentum_period': 5,       # Price momentum calculation period
            'entry_confirmation_bars': 2,     # Bars for entry confirmation
            'exit_confirmation_bars': 1       # Bars for exit confirmation
        }

        # Risk-adjusted sizing parameters
        self.sizing_config = {
            'base_position_size': 0.05,       # 5% base position size
            'max_position_size': 0.12,        # 12% maximum position
            'min_position_size': 0.02,        # 2% minimum position
            'volatility_adjustment': True,     # Adjust for volatility
            'correlation_adjustment': True,    # Adjust for portfolio correlation
            'signal_strength_multiplier': 2.0 # Maximum signal strength multiplier
        }

    def get_current_market_data(self, symbol):
        """Get current market data for signal generation"""
        with self.db.get_connection() as conn:
            # Get recent price data
            cursor = conn.execute("""
                SELECT date, open, high, low, close, volume FROM price_data
                WHERE stock_symbol = ?
                ORDER BY date DESC
                LIMIT 30
            """, (symbol,))

            data = cursor.fetchall()
            if not data:
                return None

            df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
            df = df.sort_index()  # Ensure chronological order

            return df

    def calculate_support_resistance(self, price_data, levels=3):
        """Calculate key support and resistance levels"""
        if len(price_data) < 10:
            return {'support': [], 'resistance': []}

        highs = price_data['high'].values
        lows = price_data['low'].values
        closes = price_data['close'].values

        # Find pivot points
        resistance_candidates = []
        support_candidates = []

        # Local maxima (resistance)
        for i in range(2, len(highs) - 2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                resistance_candidates.append(highs[i])

        # Local minima (support)
        for i in range(2, len(lows) - 2):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                support_candidates.append(lows[i])

        # Select most significant levels
        current_price = closes[-1]

        # Resistance levels above current price
        resistance_levels = sorted([r for r in resistance_candidates if r > current_price])[:levels]

        # Support levels below current price
        support_levels = sorted([s for s in support_candidates if s < current_price], reverse=True)[:levels]

        return {
            'support': support_levels,
            'resistance': resistance_levels,
            'current_price': current_price
        }

    def calculate_entry_precision(self, symbol, signal_strength, signal_direction):
        """Calculate precise entry timing and levels"""
        price_data = self.get_current_market_data(symbol)
        if price_data is None or len(price_data) < 10:
            return None

        current_price = price_data['close'].iloc[-1]

        # Calculate technical indicators for precision
        price_data['sma_5'] = price_data['close'].rolling(5).mean()
        price_data['sma_10'] = price_data['close'].rolling(10).mean()
        price_data['rsi'] = self.calculate_rsi(price_data['close'], 14)

        # Volume analysis
        avg_volume = price_data['volume'].rolling(10).mean().iloc[-1]
        current_volume = price_data['volume'].iloc[-1]
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1

        # Volatility (ATR)
        atr = self.calculate_atr(price_data, 14)

        # Support/Resistance levels
        sr_levels = self.calculate_support_resistance(price_data)

        # Entry signal precision
        entry_signals = {
            'signal_strength': signal_strength,
            'signal_direction': signal_direction,
            'current_price': current_price,
            'entry_price': current_price,  # Will be refined below
            'stop_loss': None,
            'take_profit_1': None,
            'take_profit_2': None,
            'confidence': 0,
            'urgency': 'Normal',
            'risk_reward_ratio': 0,
            'technical_confluence': 0
        }

        if signal_direction in ['Buy', 'Strong Buy']:
            # Buy signal precision
            confluence_score = 0

            # Price above moving averages
            if current_price > price_data['sma_5'].iloc[-1]:
                confluence_score += 1
            if current_price > price_data['sma_10'].iloc[-1]:
                confluence_score += 1

            # RSI conditions
            rsi_current = price_data['rsi'].iloc[-1]
            if 40 <= rsi_current <= 70:  # Not overbought/oversold
                confluence_score += 1

            # Volume confirmation
            if volume_ratio >= self.precision_config['volume_surge_threshold']:
                confluence_score += 2
            elif volume_ratio >= 1.2:
                confluence_score += 1

            # Support level proximity
            if sr_levels['support']:
                nearest_support = max(sr_levels['support'])
                support_distance = (current_price - nearest_support) / current_price
                if support_distance <= 0.03:  # Within 3% of support
                    confluence_score += 2

            # Entry price refinement
            if confluence_score >= 3:
                entry_signals['entry_price'] = current_price
                entry_signals['urgency'] = 'High' if confluence_score >= 5 else 'Medium'
            else:
                # Wait for better entry near support
                if sr_levels['support']:
                    entry_signals['entry_price'] = max(sr_levels['support']) * 1.005  # 0.5% above support

            # Risk management levels
            if sr_levels['support']:
                entry_signals['stop_loss'] = max(sr_levels['support']) * 0.98  # 2% below support
            else:
                entry_signals['stop_loss'] = current_price * (1 - atr / current_price * 2)

            # Take profit levels
            if sr_levels['resistance']:
                entry_signals['take_profit_1'] = min(sr_levels['resistance']) * 0.98  # Just below resistance
                if len(sr_levels['resistance']) > 1:
                    entry_signals['take_profit_2'] = sr_levels['resistance'][1] * 0.98
            else:
                entry_signals['take_profit_1'] = current_price * (1 + atr / current_price * 3)
                entry_signals['take_profit_2'] = current_price * (1 + atr / current_price * 5)

            entry_signals['technical_confluence'] = confluence_score

        elif signal_direction in ['Sell', 'Strong Sell']:
            # Sell signal precision (inverse logic)
            confluence_score = 0

            # Price below moving averages
            if current_price < price_data['sma_5'].iloc[-1]:
                confluence_score += 1
            if current_price < price_data['sma_10'].iloc[-1]:
                confluence_score += 1

            # RSI conditions
            rsi_current = price_data['rsi'].iloc[-1]
            if rsi_current >= 70 or rsi_current <= 30:  # Overbought/oversold
                confluence_score += 2

            # Volume confirmation
            if volume_ratio >= self.precision_config['volume_surge_threshold']:
                confluence_score += 2

            # Resistance level proximity
            if sr_levels['resistance']:
                nearest_resistance = min(sr_levels['resistance'])
                resistance_distance = (nearest_resistance - current_price) / current_price
                if resistance_distance <= 0.03:  # Within 3% of resistance
                    confluence_score += 2

            entry_signals['technical_confluence'] = confluence_score
            entry_signals['urgency'] = 'High' if confluence_score >= 4 else 'Medium'

        # Calculate confidence and risk-reward ratio
        if entry_signals['stop_loss'] and entry_signals['take_profit_1']:
            risk = abs(entry_signals['entry_price'] - entry_signals['stop_loss'])
            reward = abs(entry_signals['take_profit_1'] - entry_signals['entry_price'])
            entry_signals['risk_reward_ratio'] = reward / risk if risk > 0 else 0

        # Overall confidence score
        base_confidence = min(signal_strength / 100, 1.0)
        technical_bonus = min(entry_signals['technical_confluence'] / 6, 0.3)
        volume_bonus = min((volume_ratio - 1) / 3, 0.2)

        entry_signals['confidence'] = min(base_confidence + technical_bonus + volume_bonus, 1.0)

        return entry_signals

    def calculate_rsi(self, prices, period=14):
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)

        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_atr(self, price_data, period=14):
        """Calculate Average True Range"""
        high_low = price_data['high'] - price_data['low']
        high_close = np.abs(price_data['high'] - price_data['close'].shift())
        low_close = np.abs(price_data['low'] - price_data['close'].shift())

        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=period).mean().iloc[-1]

        return atr if not np.isnan(atr) else price_data['close'].iloc[-1] * 0.02

    def generate_position_sizing(self, symbol, entry_price, signal_strength, portfolio_value):
        """Generate risk-adjusted position sizing recommendation"""
        # Get volatility
        volatility = self.risk_manager.calculate_position_volatility(symbol)

        # Base position size
        base_size = self.sizing_config['base_position_size']

        # Signal strength adjustment
        strength_factor = (signal_strength - 50) / 50  # -1 to 1
        strength_multiplier = 1 + (strength_factor * 0.5)  # 0.5 to 1.5

        # Volatility adjustment
        vol_adjustment = min(0.25 / max(volatility, 0.1), 1.5) if self.sizing_config['volatility_adjustment'] else 1.0

        # Calculate position size
        position_size = base_size * strength_multiplier * vol_adjustment

        # Apply limits
        position_size = max(self.sizing_config['min_position_size'], position_size)
        position_size = min(self.sizing_config['max_position_size'], position_size)

        # Calculate actual values
        position_value = portfolio_value * position_size
        shares = int(position_value / entry_price)
        actual_position_value = shares * entry_price
        actual_position_size = actual_position_value / portfolio_value

        return {
            'position_size_pct': actual_position_size,
            'position_value': actual_position_value,
            'shares': shares,
            'volatility': volatility,
            'strength_multiplier': strength_multiplier,
            'vol_adjustment': vol_adjustment
        }

    def generate_real_time_signals(self, symbols=None, portfolio_value=1000000000):
        """Generate comprehensive real-time trading signals"""
        if symbols is None:
            stocks = self.db.get_all_stocks()
            symbols = [stock['symbol'] for stock in stocks]

        signals = []

        print(f"Generating real-time signals for {len(symbols)} stocks...")

        for symbol in symbols:
            try:
                # Get smart money analysis
                analysis = self.analyzer.analyze_symbol(symbol, days_back=60)

                if 'error' in analysis:
                    continue

                signal_strength = analysis['market_context']['adjusted_score']
                signal_class = analysis['composite_score']['signal_class']

                # Determine signal direction
                if signal_strength >= self.signal_config['strong_buy_threshold']:
                    signal_direction = 'Strong Buy'
                elif signal_strength >= self.signal_config['buy_threshold']:
                    signal_direction = 'Buy'
                elif signal_strength >= self.signal_config['weak_buy_threshold']:
                    signal_direction = 'Weak Buy'
                elif signal_strength <= self.signal_config['strong_sell_threshold']:
                    signal_direction = 'Strong Sell'
                elif signal_strength <= self.signal_config['sell_threshold']:
                    signal_direction = 'Sell'
                elif signal_strength <= self.signal_config['weak_sell_threshold']:
                    signal_direction = 'Weak Sell'
                else:
                    signal_direction = 'Hold'

                # Skip hold signals for efficiency
                if signal_direction == 'Hold':
                    continue

                # Get precise entry/exit levels
                entry_precision = self.calculate_entry_precision(symbol, signal_strength, signal_direction)

                if entry_precision is None:
                    continue

                # Generate position sizing
                position_sizing = self.generate_position_sizing(
                    symbol, entry_precision['entry_price'], signal_strength, portfolio_value
                )

                # Compile signal
                signal = {
                    'symbol': symbol,
                    'timestamp': datetime.now(),
                    'signal_direction': signal_direction,
                    'signal_strength': signal_strength,
                    'signal_class': signal_class,
                    'confidence': entry_precision['confidence'],
                    'urgency': entry_precision['urgency'],
                    'entry_price': entry_precision['entry_price'],
                    'current_price': entry_precision['current_price'],
                    'stop_loss': entry_precision['stop_loss'],
                    'take_profit_1': entry_precision['take_profit_1'],
                    'take_profit_2': entry_precision['take_profit_2'],
                    'risk_reward_ratio': entry_precision['risk_reward_ratio'],
                    'technical_confluence': entry_precision['technical_confluence'],
                    'position_size_pct': position_sizing['position_size_pct'],
                    'position_value': position_sizing['position_value'],
                    'shares': position_sizing['shares'],
                    'volatility': position_sizing['volatility'],
                    'components': analysis['composite_score']['component_scores']
                }

                signals.append(signal)

            except Exception as e:
                print(f"  Error processing {symbol}: {e}")
                continue

        # Sort by confidence and signal strength
        signals.sort(key=lambda x: (x['confidence'], x['signal_strength']), reverse=True)

        return signals

    def filter_high_probability_signals(self, signals, min_confidence=0.7, min_rr_ratio=2.0):
        """Filter for high-probability trading setups"""
        high_prob_signals = []

        for signal in signals:
            # Quality filters
            if (signal['confidence'] >= min_confidence and
                signal['risk_reward_ratio'] >= min_rr_ratio and
                signal['technical_confluence'] >= 3 and
                signal['urgency'] in ['High', 'Medium']):

                high_prob_signals.append(signal)

        return high_prob_signals

def main():
    """Test real-time signal generation"""
    print("Vietnam Stock Analysis - Real-Time Trading Signals")
    print("=" * 70)

    signal_generator = VietnameseTradingSignals()

    try:
        print("Generating real-time trading signals...")

        # Generate signals for top stocks
        test_symbols = ['VCB', 'HPG', 'VHM', 'CTG', 'BID', 'VIC', 'MBB']
        signals = signal_generator.generate_real_time_signals(test_symbols)

        print(f"\n📊 Generated {len(signals)} active signals")

        if signals:
            print(f"\n🎯 Top Trading Signals:")
            for i, signal in enumerate(signals[:5], 1):
                print(f"\n  {i}. {signal['symbol']} - {signal['signal_direction']}")
                print(f"     Strength: {signal['signal_strength']:.1f} | Confidence: {signal['confidence']:.1%}")
                print(f"     Entry: {signal['entry_price']:,.0f} VND | Stop: {signal['stop_loss']:,.0f} VND")
                print(f"     Target 1: {signal['take_profit_1']:,.0f} VND | R:R {signal['risk_reward_ratio']:.1f}")
                print(f"     Position: {signal['position_size_pct']:.1%} ({signal['shares']:,} shares)")
                print(f"     Urgency: {signal['urgency']} | Confluence: {signal['technical_confluence']}/6")

        # Filter for high-probability setups
        high_prob = signal_generator.filter_high_probability_signals(signals)

        print(f"\n🔥 High-Probability Setups: {len(high_prob)}")
        for signal in high_prob:
            print(f"  • {signal['symbol']}: {signal['signal_direction']} "
                  f"(Conf: {signal['confidence']:.1%}, R:R: {signal['risk_reward_ratio']:.1f})")

        print(f"\n✅ Real-time signal generation completed!")

    except Exception as e:
        print(f"❌ Signal generation error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()