#!/usr/bin/env python3
"""
Risk Management System
Advanced risk controls for Vietnamese stock trading with correlation analysis
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

class VietnameseRiskManager:
    """Advanced risk management for Vietnamese market trading"""

    def __init__(self):
        self.db = get_db()
        self.analyzer = SmartMoneyAnalyzer()

        # Vietnamese market risk parameters
        self.risk_limits = {
            'max_portfolio_risk': 0.20,       # Maximum 20% portfolio volatility
            'max_position_risk': 0.05,        # Maximum 5% risk per position
            'max_sector_risk': 0.12,          # Maximum 12% risk per sector
            'max_daily_loss': 0.03,           # Maximum 3% daily loss
            'correlation_threshold': 0.7,      # High correlation warning
            'concentration_limit': 0.15,      # Maximum 15% in single position
            'stop_loss_multiplier': 2.0,      # 2x ATR for stop loss
            'max_drawdown': 0.15              # Maximum 15% drawdown
        }

        # Position sizing parameters
        self.position_sizing = {
            'base_risk_per_trade': 0.02,      # 2% base risk per trade
            'volatility_adjustment': True,     # Adjust for volatility
            'correlation_adjustment': True,    # Adjust for correlation
            'signal_strength_multiplier': 1.5, # Up to 1.5x for strong signals
            'min_position_size': 0.01,        # Minimum 1% position
            'max_position_size': 0.08         # Maximum 8% position (before adjustments)
        }

        # Stop loss parameters
        self.stop_loss_config = {
            'atr_period': 14,                 # ATR calculation period
            'atr_multiplier': 2.0,            # ATR multiplier for stop loss
            'min_stop_distance': 0.03,        # Minimum 3% stop distance
            'max_stop_distance': 0.12,        # Maximum 12% stop distance
            'signal_based_adjustment': True,   # Adjust based on signal strength
            'trailing_stop_activation': 0.05  # Activate trailing stop at 5% profit
        }

    def get_portfolio_data(self):
        """Get current portfolio positions"""
        portfolio = self.db.get_portfolio_performance()
        return portfolio

    def calculate_position_volatility(self, symbol, days_back=30):
        """Calculate individual stock volatility"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT close FROM price_data
                WHERE stock_symbol = ?
                ORDER BY date DESC
                LIMIT ?
            """, (symbol, days_back + 1))

            prices = [row[0] for row in cursor.fetchall()]

        if len(prices) < 10:
            return 0.25  # Default high volatility for insufficient data

        # Calculate daily returns
        returns = []
        for i in range(1, len(prices)):
            returns.append((prices[i-1] - prices[i]) / prices[i])

        if returns:
            volatility = np.std(returns) * np.sqrt(252)  # Annualized
            return volatility
        else:
            return 0.25

    def calculate_atr(self, symbol, period=14):
        """Calculate Average True Range for stop loss calculation"""
        with self.db.get_connection() as conn:
            cursor = conn.execute("""
                SELECT high, low, close FROM price_data
                WHERE stock_symbol = ?
                ORDER BY date DESC
                LIMIT ?
            """, (symbol, period + 1))

            data = cursor.fetchall()

        if len(data) < period:
            # Fallback to volatility-based calculation
            volatility = self.calculate_position_volatility(symbol)
            return volatility * 0.15  # Approximate ATR as 15% of volatility

        true_ranges = []
        for i in range(1, len(data)):
            high, low, close = data[i-1][0], data[i-1][1], data[i-1][2]
            prev_close = data[i][2]

            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)

            true_range = max(tr1, tr2, tr3)
            true_ranges.append(true_range)

        if true_ranges:
            return np.mean(true_ranges)
        else:
            return 0.05  # Default 5% ATR

    def calculate_correlation_matrix(self, symbols, days_back=60):
        """Calculate correlation matrix for portfolio positions"""
        price_data = {}

        with self.db.get_connection() as conn:
            for symbol in symbols:
                cursor = conn.execute("""
                    SELECT date, close FROM price_data
                    WHERE stock_symbol = ?
                    ORDER BY date DESC
                    LIMIT ?
                """, (symbol, days_back))

                data = cursor.fetchall()
                if data:
                    dates = [row[0] for row in data]
                    prices = [row[1] for row in data]
                    price_data[symbol] = pd.Series(prices, index=dates)

        if len(price_data) < 2:
            return pd.DataFrame()

        # Create DataFrame and calculate returns
        df = pd.DataFrame(price_data).sort_index()
        returns = df.pct_change().dropna()

        # Calculate correlation matrix
        correlation_matrix = returns.corr()
        return correlation_matrix

    def calculate_position_size(self, symbol, entry_price, account_value, signal_strength=50):
        """Calculate optimal position size with risk adjustments"""
        # Base risk calculation
        base_risk = self.position_sizing['base_risk_per_trade']

        # Volatility adjustment
        volatility = self.calculate_position_volatility(symbol)
        if self.position_sizing['volatility_adjustment']:
            # Higher volatility = smaller position
            vol_adjustment = min(0.25 / max(volatility, 0.1), 2.0)  # Cap adjustment
        else:
            vol_adjustment = 1.0

        # Signal strength adjustment
        signal_normalized = (signal_strength - 50) / 50  # Convert to -1 to 1
        signal_multiplier = 1.0 + (signal_normalized * 0.5)  # 0.5 to 1.5 multiplier
        signal_multiplier = max(0.5, min(signal_multiplier, self.position_sizing['signal_strength_multiplier']))

        # Calculate stop loss distance for position sizing
        atr = self.calculate_atr(symbol)
        stop_distance = max(
            atr * self.stop_loss_config['atr_multiplier'] / entry_price,
            self.stop_loss_config['min_stop_distance']
        )
        stop_distance = min(stop_distance, self.stop_loss_config['max_stop_distance'])

        # Position size calculation: Risk Amount / Stop Distance
        risk_amount = account_value * base_risk * vol_adjustment * signal_multiplier
        position_value = risk_amount / stop_distance

        # Convert to percentage of account
        position_size_pct = position_value / account_value

        # Apply limits
        position_size_pct = max(self.position_sizing['min_position_size'], position_size_pct)
        position_size_pct = min(self.position_sizing['max_position_size'], position_size_pct)

        return {
            'position_size_pct': position_size_pct,
            'position_value': position_value,
            'shares': int(position_value / entry_price),
            'risk_amount': risk_amount,
            'stop_distance': stop_distance,
            'stop_price': entry_price * (1 - stop_distance),
            'volatility': volatility,
            'signal_multiplier': signal_multiplier,
            'vol_adjustment': vol_adjustment
        }

    def calculate_stop_loss(self, symbol, entry_price, position_type='long', signal_strength=50):
        """Calculate dynamic stop loss based on ATR and signal strength"""
        atr = self.calculate_atr(symbol)
        atr_multiplier = self.stop_loss_config['atr_multiplier']

        # Adjust multiplier based on signal strength
        if self.stop_loss_config['signal_based_adjustment']:
            # Stronger signals get tighter stops (more confidence)
            strength_factor = (signal_strength - 50) / 50  # -1 to 1
            atr_multiplier = atr_multiplier * (1 - strength_factor * 0.3)  # ±30% adjustment

        # Calculate stop distance
        stop_distance = atr * atr_multiplier / entry_price

        # Apply limits
        stop_distance = max(stop_distance, self.stop_loss_config['min_stop_distance'])
        stop_distance = min(stop_distance, self.stop_loss_config['max_stop_distance'])

        if position_type == 'long':
            stop_price = entry_price * (1 - stop_distance)
        else:  # short
            stop_price = entry_price * (1 + stop_distance)

        return {
            'stop_price': stop_price,
            'stop_distance_pct': stop_distance,
            'atr': atr,
            'atr_multiplier': atr_multiplier
        }

    def assess_portfolio_risk(self, positions=None):
        """Comprehensive portfolio risk assessment"""
        if positions is None:
            portfolio = self.get_portfolio_data()
            positions = portfolio['positions']

        if not positions:
            return {'total_risk': 0, 'risk_breakdown': {}, 'warnings': []}

        symbols = [pos.get('symbol', pos.get('stock_symbol', '')) for pos in positions]
        symbols = [s for s in symbols if s]  # Filter out empty strings

        if not symbols:
            return {'total_risk': 0, 'risk_breakdown': {}, 'warnings': ['No valid positions found']}

        # Calculate correlation matrix
        correlation_matrix = self.calculate_correlation_matrix(symbols)

        # Calculate total portfolio value for weight calculation
        total_portfolio_value = sum(pos.get('position_value', pos.get('value', 0)) for pos in positions)

        # Individual position risks
        position_risks = {}
        sector_risks = {}
        weights = {}

        for position in positions:
            symbol = position.get('symbol', position.get('stock_symbol', ''))
            if not symbol:
                continue

            # Calculate weight from position value
            position_value = position.get('position_value', position.get('value', 0))
            weight = position_value / total_portfolio_value if total_portfolio_value > 0 else 0
            weights[symbol] = weight

            # Individual risk
            volatility = self.calculate_position_volatility(symbol)
            position_risk = weight * volatility
            position_risks[symbol] = position_risk

            # Sector risk aggregation
            sector = position.get('sector', 'Unknown')
            if sector not in sector_risks:
                sector_risks[sector] = 0
            sector_risks[sector] += position_risk

        # Portfolio variance calculation with correlations
        if not correlation_matrix.empty and len(symbols) > 1:
            portfolio_variance = 0
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols):
                    if symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns:
                        weight1 = weights[symbol1]
                        weight2 = weights[symbol2]
                        vol1 = self.calculate_position_volatility(symbol1)
                        vol2 = self.calculate_position_volatility(symbol2)
                        correlation = correlation_matrix.loc[symbol1, symbol2]

                        portfolio_variance += weight1 * weight2 * vol1 * vol2 * correlation

            portfolio_risk = np.sqrt(max(portfolio_variance, 0))
        else:
            # Fallback to simple weighted average
            portfolio_risk = sum(position_risks.values())

        # Risk warnings
        warnings = []

        # Check portfolio risk limit
        if portfolio_risk > self.risk_limits['max_portfolio_risk']:
            warnings.append(f"Portfolio risk ({portfolio_risk:.1%}) exceeds limit ({self.risk_limits['max_portfolio_risk']:.1%})")

        # Check position concentration
        for symbol, risk in position_risks.items():
            if risk > self.risk_limits['max_position_risk']:
                warnings.append(f"{symbol} risk ({risk:.1%}) exceeds position limit ({self.risk_limits['max_position_risk']:.1%})")

        # Check sector concentration
        for sector, risk in sector_risks.items():
            if risk > self.risk_limits['max_sector_risk']:
                warnings.append(f"{sector} sector risk ({risk:.1%}) exceeds limit ({self.risk_limits['max_sector_risk']:.1%})")

        # Check high correlations
        if not correlation_matrix.empty:
            for i, symbol1 in enumerate(symbols):
                for j, symbol2 in enumerate(symbols[i+1:], i+1):
                    if symbol1 in correlation_matrix.index and symbol2 in correlation_matrix.columns:
                        correlation = correlation_matrix.loc[symbol1, symbol2]
                        if abs(correlation) > self.risk_limits['correlation_threshold']:
                            warnings.append(f"High correlation between {symbol1} and {symbol2}: {correlation:.2f}")

        return {
            'total_risk': portfolio_risk,
            'position_risks': position_risks,
            'sector_risks': sector_risks,
            'correlation_matrix': correlation_matrix,
            'warnings': warnings,
            'risk_utilization': portfolio_risk / self.risk_limits['max_portfolio_risk'],
            'diversification_ratio': len(symbols) / max(len(set(pos.get('sector', 'Unknown') for pos in positions)), 1)
        }

    def generate_risk_report(self, symbol=None, entry_price=None, account_value=100000):
        """Generate comprehensive risk management report"""
        print("=== Vietnamese Market Risk Management Report ===")

        if symbol and entry_price:
            # Individual position analysis
            print(f"\n📊 Position Analysis: {symbol}")

            # Get smart money signal
            try:
                analysis = self.analyzer.analyze_symbol(symbol, days_back=60)
                signal_strength = analysis['market_context']['adjusted_score'] if 'error' not in analysis else 50
                signal_class = analysis['composite_score']['signal_class'] if 'error' not in analysis else 'Hold'
            except:
                signal_strength = 50
                signal_class = 'Hold'

            # Position sizing
            position_info = self.calculate_position_size(symbol, entry_price, account_value, signal_strength)
            stop_info = self.calculate_stop_loss(symbol, entry_price, 'long', signal_strength)

            print(f"  Entry Price: {entry_price:,.0f} VND")
            print(f"  Signal: {signal_class} (Score: {signal_strength:.1f})")
            print(f"  Recommended Position: {position_info['position_size_pct']:.1%} of portfolio")
            print(f"  Shares: {position_info['shares']:,}")
            print(f"  Position Value: {position_info['position_value']:,.0f} VND")
            print(f"  Risk Amount: {position_info['risk_amount']:,.0f} VND ({position_info['risk_amount']/account_value:.1%})")
            print(f"  Stop Loss: {stop_info['stop_price']:,.0f} VND ({stop_info['stop_distance_pct']:.1%} distance)")
            print(f"  Volatility: {position_info['volatility']:.1%}")

        # Portfolio risk assessment
        portfolio_risk = self.assess_portfolio_risk()

        print(f"\n📈 Portfolio Risk Analysis:")
        print(f"  Total Portfolio Risk: {portfolio_risk['total_risk']:.1%}")
        print(f"  Risk Utilization: {portfolio_risk['risk_utilization']:.1%}")
        print(f"  Diversification Ratio: {portfolio_risk['diversification_ratio']:.1f}")

        if portfolio_risk['position_risks']:
            print(f"\n🎯 Position Risk Breakdown:")
            for symbol, risk in sorted(portfolio_risk['position_risks'].items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {symbol}: {risk:.1%}")

        if portfolio_risk['sector_risks']:
            print(f"\n🏢 Sector Risk Breakdown:")
            for sector, risk in sorted(portfolio_risk['sector_risks'].items(), key=lambda x: x[1], reverse=True):
                print(f"    {sector.replace('_', ' ').title()}: {risk:.1%}")

        if portfolio_risk['warnings']:
            print(f"\n⚠️ Risk Warnings:")
            for warning in portfolio_risk['warnings']:
                print(f"    • {warning}")

        return portfolio_risk

def main():
    """Test risk management system"""
    print("Vietnam Stock Analysis - Risk Management System")
    print("=" * 70)

    risk_manager = VietnameseRiskManager()

    try:
        # Test with VCB position
        symbol = "VCB"
        entry_price = 85000  # Example entry price
        account_value = 1000000000  # 1 billion VND

        print(f"Testing risk management for {symbol} position...")

        risk_report = risk_manager.generate_risk_report(symbol, entry_price, account_value)

        print(f"\n✅ Risk management analysis completed!")

        # Risk scoring
        total_risk = risk_report['total_risk']
        risk_utilization = risk_report['risk_utilization']

        print(f"\n🎯 Risk Management Score:")
        if total_risk < 0.15 and risk_utilization < 0.8:
            print("  ✅ CONSERVATIVE: Well-controlled risk profile")
        elif total_risk < 0.20 and risk_utilization < 1.0:
            print("  ⚠️ MODERATE: Acceptable risk levels")
        else:
            print("  ❌ AGGRESSIVE: High risk - consider reducing exposure")

    except Exception as e:
        print(f"❌ Risk management error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()