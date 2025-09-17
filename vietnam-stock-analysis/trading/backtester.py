#!/usr/bin/env python3
"""
Strategy Backtesting Framework
Historical validation of smart money signals for Vietnamese market trading
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

class VietnameseBacktester:
    """Comprehensive backtesting framework for Vietnamese smart money strategies"""

    def __init__(self):
        self.db = get_db()
        self.analyzer = SmartMoneyAnalyzer()
        self.risk_manager = VietnameseRiskManager()

        # Backtesting parameters
        self.config = {
            'initial_capital': 1000000000,     # 1 billion VND
            'commission_rate': 0.0015,         # 0.15% commission
            'slippage': 0.001,                 # 0.1% slippage
            'max_positions': 10,               # Maximum concurrent positions
            'rebalance_frequency': 5,          # Rebalance every 5 days
            'lookback_period': 60,             # Signal lookback period
            'min_trade_amount': 50000000,      # Minimum 50M VND per trade
            'transaction_cost': 0.002          # Total transaction cost (commission + slippage)
        }

        # Strategy parameters
        self.strategy_config = {
            'buy_threshold': 60,               # Buy signal threshold
            'sell_threshold': 45,              # Sell signal threshold
            'strong_buy_threshold': 70,        # Strong buy threshold
            'stop_loss_pct': 0.08,            # 8% stop loss
            'take_profit_pct': 0.15,          # 15% take profit
            'holding_period_max': 30,          # Maximum 30 days holding
            'min_signal_strength': 52,         # Minimum signal strength to trade
            'position_sizing_method': 'equal_weight'  # equal_weight, risk_parity, smart_weight
        }

    def get_historical_data(self, symbols, start_date, end_date):
        """Get historical price data for backtesting"""
        historical_data = {}

        with self.db.get_connection() as conn:
            for symbol in symbols:
                cursor = conn.execute("""
                    SELECT date, open, high, low, close, volume FROM price_data
                    WHERE stock_symbol = ? AND date BETWEEN ? AND ?
                    ORDER BY date ASC
                """, (symbol, start_date, end_date))

                data = cursor.fetchall()
                if data:
                    df = pd.DataFrame(data, columns=['date', 'open', 'high', 'low', 'close', 'volume'])
                    df['date'] = pd.to_datetime(df['date'])
                    df.set_index('date', inplace=True)
                    historical_data[symbol] = df

        return historical_data

    def generate_signals(self, symbol, date, historical_data):
        """Generate trading signals for a specific date"""
        if symbol not in historical_data:
            return {'signal': 'Hold', 'strength': 50, 'confidence': 0}

        # Get data up to current date
        symbol_data = historical_data[symbol][historical_data[symbol].index <= date]

        if len(symbol_data) < self.config['lookback_period']:
            return {'signal': 'Hold', 'strength': 50, 'confidence': 0}

        try:
            # Use smart money analyzer with historical context
            analysis = self.analyzer.analyze_symbol(symbol, days_back=self.config['lookback_period'])

            if 'error' not in analysis:
                signal_strength = analysis['market_context']['adjusted_score']
                signal_class = analysis['composite_score']['signal_class']
                confidence = min(abs(signal_strength - 50) / 50, 1.0)  # Normalize confidence

                # Map signal class to buy/sell/hold
                if signal_strength >= self.strategy_config['strong_buy_threshold']:
                    signal = 'Strong Buy'
                elif signal_strength >= self.strategy_config['buy_threshold']:
                    signal = 'Buy'
                elif signal_strength <= self.strategy_config['sell_threshold']:
                    signal = 'Sell'
                else:
                    signal = 'Hold'

                return {
                    'signal': signal,
                    'strength': signal_strength,
                    'confidence': confidence,
                    'components': analysis['composite_score']['component_scores']
                }
            else:
                return {'signal': 'Hold', 'strength': 50, 'confidence': 0}

        except Exception as e:
            return {'signal': 'Hold', 'strength': 50, 'confidence': 0, 'error': str(e)}

    def calculate_position_size(self, signal_data, current_price, available_capital, portfolio_value):
        """Calculate position size based on strategy configuration"""
        if self.strategy_config['position_sizing_method'] == 'equal_weight':
            max_position_value = portfolio_value / self.config['max_positions']

        elif self.strategy_config['position_sizing_method'] == 'smart_weight':
            # Adjust position size based on signal strength
            base_position = portfolio_value / self.config['max_positions']
            signal_multiplier = signal_data['strength'] / 50  # 0.9 to 1.6 range
            max_position_value = base_position * signal_multiplier

        elif self.strategy_config['position_sizing_method'] == 'risk_parity':
            # Risk-based position sizing (simplified)
            max_position_value = portfolio_value * 0.02 / self.strategy_config['stop_loss_pct']

        else:
            max_position_value = portfolio_value / self.config['max_positions']

        # Ensure position meets minimum requirements
        position_value = min(max_position_value, available_capital)
        position_value = max(position_value, self.config['min_trade_amount'])

        # Calculate shares
        shares = int(position_value / current_price)
        actual_position_value = shares * current_price

        return {
            'shares': shares,
            'position_value': actual_position_value,
            'position_pct': actual_position_value / portfolio_value if portfolio_value > 0 else 0
        }

    def execute_trade(self, symbol, action, shares, price, date, reason=""):
        """Execute a trade and return trade details"""
        if shares <= 0:
            return None

        gross_value = shares * price
        transaction_cost = gross_value * self.config['transaction_cost']
        net_value = gross_value + transaction_cost if action == 'buy' else gross_value - transaction_cost

        trade = {
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price,
            'gross_value': gross_value,
            'transaction_cost': transaction_cost,
            'net_value': net_value,
            'date': date,
            'reason': reason
        }

        return trade

    def run_backtest(self, symbols, start_date, end_date):
        """Run comprehensive backtest on given symbols and date range"""
        print(f"=== Running Backtest: {start_date} to {end_date} ===")
        print(f"Symbols: {symbols}")
        print(f"Initial Capital: {self.config['initial_capital']:,.0f} VND")

        # Get historical data
        print("Loading historical data...")
        historical_data = self.get_historical_data(symbols, start_date, end_date)

        if not historical_data:
            raise ValueError("No historical data available for backtesting")

        # Initialize portfolio tracking
        portfolio = {
            'cash': self.config['initial_capital'],
            'positions': {},  # symbol: {'shares': int, 'entry_price': float, 'entry_date': date}
            'total_value': self.config['initial_capital'],
            'max_value': self.config['initial_capital'],
            'max_drawdown': 0
        }

        # Trading log
        trades = []
        daily_portfolio_values = []
        signal_history = []

        # Get all trading dates
        all_dates = set()
        for symbol_data in historical_data.values():
            all_dates.update(symbol_data.index)
        trading_dates = sorted(list(all_dates))

        print(f"Backtesting {len(trading_dates)} trading days...")

        # Daily backtesting loop
        for i, current_date in enumerate(trading_dates):
            daily_signals = {}

            # Generate signals for all symbols
            for symbol in symbols:
                if symbol in historical_data and current_date in historical_data[symbol].index:
                    signal_data = self.generate_signals(symbol, current_date, historical_data)
                    daily_signals[symbol] = signal_data

            # Update portfolio value with current prices
            portfolio_value = portfolio['cash']
            for symbol, position in portfolio['positions'].items():
                if symbol in historical_data and current_date in historical_data[symbol].index:
                    current_price = historical_data[symbol].loc[current_date, 'close']
                    position_value = position['shares'] * current_price
                    portfolio_value += position_value

            portfolio['total_value'] = portfolio_value

            # Track maximum value and drawdown
            if portfolio_value > portfolio['max_value']:
                portfolio['max_value'] = portfolio_value

            current_drawdown = (portfolio['max_value'] - portfolio_value) / portfolio['max_value']
            if current_drawdown > portfolio['max_drawdown']:
                portfolio['max_drawdown'] = current_drawdown

            # Execute trades based on signals
            for symbol, signal_data in daily_signals.items():
                if symbol not in historical_data or current_date not in historical_data[symbol].index:
                    continue

                current_price = historical_data[symbol].loc[current_date, 'close']
                signal = signal_data['signal']
                strength = signal_data['strength']

                # Check if we should buy
                if signal in ['Buy', 'Strong Buy'] and symbol not in portfolio['positions']:
                    if strength >= self.strategy_config['min_signal_strength']:
                        # Calculate position size
                        position_info = self.calculate_position_size(
                            signal_data, current_price, portfolio['cash'], portfolio_value
                        )

                        if position_info['shares'] > 0 and position_info['position_value'] <= portfolio['cash']:
                            # Execute buy trade
                            trade = self.execute_trade(
                                symbol, 'buy', position_info['shares'], current_price,
                                current_date, f"{signal} signal (strength: {strength:.1f})"
                            )

                            if trade:
                                trades.append(trade)
                                portfolio['cash'] -= trade['net_value']
                                portfolio['positions'][symbol] = {
                                    'shares': trade['shares'],
                                    'entry_price': trade['price'],
                                    'entry_date': current_date,
                                    'stop_loss': trade['price'] * (1 - self.strategy_config['stop_loss_pct']),
                                    'take_profit': trade['price'] * (1 + self.strategy_config['take_profit_pct'])
                                }

                # Check if we should sell existing positions
                elif symbol in portfolio['positions']:
                    position = portfolio['positions'][symbol]
                    days_held = (current_date - position['entry_date']).days

                    # Sell conditions
                    should_sell = False
                    sell_reason = ""

                    # Stop loss
                    if current_price <= position['stop_loss']:
                        should_sell = True
                        sell_reason = f"Stop loss (price: {current_price:.0f}, stop: {position['stop_loss']:.0f})"

                    # Take profit
                    elif current_price >= position['take_profit']:
                        should_sell = True
                        sell_reason = f"Take profit (price: {current_price:.0f}, target: {position['take_profit']:.0f})"

                    # Signal-based exit
                    elif signal == 'Sell' and strength <= self.strategy_config['sell_threshold']:
                        should_sell = True
                        sell_reason = f"Sell signal (strength: {strength:.1f})"

                    # Maximum holding period
                    elif days_held >= self.strategy_config['holding_period_max']:
                        should_sell = True
                        sell_reason = f"Max holding period ({days_held} days)"

                    if should_sell:
                        # Execute sell trade
                        trade = self.execute_trade(
                            symbol, 'sell', position['shares'], current_price,
                            current_date, sell_reason
                        )

                        if trade:
                            trades.append(trade)
                            portfolio['cash'] += trade['net_value']
                            del portfolio['positions'][symbol]

            # Record daily portfolio value
            daily_portfolio_values.append({
                'date': current_date,
                'portfolio_value': portfolio_value,
                'cash': portfolio['cash'],
                'positions_value': portfolio_value - portfolio['cash'],
                'num_positions': len(portfolio['positions'])
            })

            # Record signals for analysis
            signal_history.extend([{
                'date': current_date,
                'symbol': symbol,
                **signal_data
            } for symbol, signal_data in daily_signals.items()])

        # Final liquidation
        final_date = trading_dates[-1]
        for symbol, position in list(portfolio['positions'].items()):
            if symbol in historical_data and final_date in historical_data[symbol].index:
                final_price = historical_data[symbol].loc[final_date, 'close']
                trade = self.execute_trade(
                    symbol, 'sell', position['shares'], final_price,
                    final_date, "Final liquidation"
                )
                if trade:
                    trades.append(trade)
                    portfolio['cash'] += trade['net_value']

        # Calculate final portfolio value
        final_portfolio_value = portfolio['cash']
        portfolio['total_value'] = final_portfolio_value

        return self.generate_backtest_report(
            trades, daily_portfolio_values, signal_history,
            self.config['initial_capital'], final_portfolio_value
        )

    def generate_backtest_report(self, trades, daily_values, signal_history, initial_capital, final_value):
        """Generate comprehensive backtest analysis report"""
        if not daily_values:
            return {'error': 'No trading data available'}

        # Performance metrics
        total_return = (final_value - initial_capital) / initial_capital
        trading_days = len(daily_values)
        annualized_return = (1 + total_return) ** (252 / trading_days) - 1 if trading_days > 0 else 0

        # Daily returns calculation
        daily_returns = []
        for i in range(1, len(daily_values)):
            prev_value = daily_values[i-1]['portfolio_value']
            curr_value = daily_values[i]['portfolio_value']
            daily_return = (curr_value - prev_value) / prev_value if prev_value > 0 else 0
            daily_returns.append(daily_return)

        # Risk metrics
        volatility = np.std(daily_returns) * np.sqrt(252) if daily_returns else 0
        sharpe_ratio = (annualized_return - 0.06) / volatility if volatility > 0 else 0  # Assuming 6% risk-free rate

        # Maximum drawdown
        peak_value = initial_capital
        max_drawdown = 0
        for day_data in daily_values:
            if day_data['portfolio_value'] > peak_value:
                peak_value = day_data['portfolio_value']
            drawdown = (peak_value - day_data['portfolio_value']) / peak_value
            if drawdown > max_drawdown:
                max_drawdown = drawdown

        # Trade analysis
        winning_trades = []
        losing_trades = []
        trade_pairs = {}  # Group buy/sell pairs

        for trade in trades:
            if trade['action'] == 'buy':
                if trade['symbol'] not in trade_pairs:
                    trade_pairs[trade['symbol']] = []
                trade_pairs[trade['symbol']].append({'buy': trade, 'sell': None})
            else:  # sell
                # Find matching buy trade
                for pair in reversed(trade_pairs.get(trade['symbol'], [])):
                    if pair['sell'] is None:
                        pair['sell'] = trade

                        # Calculate trade P&L
                        buy_trade = pair['buy']
                        sell_trade = trade
                        profit_loss = sell_trade['net_value'] - buy_trade['net_value']
                        profit_loss_pct = profit_loss / buy_trade['net_value']

                        trade_result = {
                            'symbol': trade['symbol'],
                            'entry_date': buy_trade['date'],
                            'exit_date': sell_trade['date'],
                            'holding_days': (sell_trade['date'] - buy_trade['date']).days,
                            'entry_price': buy_trade['price'],
                            'exit_price': sell_trade['price'],
                            'shares': buy_trade['shares'],
                            'profit_loss': profit_loss,
                            'profit_loss_pct': profit_loss_pct,
                            'buy_reason': buy_trade['reason'],
                            'sell_reason': sell_trade['reason']
                        }

                        if profit_loss > 0:
                            winning_trades.append(trade_result)
                        else:
                            losing_trades.append(trade_result)
                        break

        # Trading statistics
        total_trades = len(winning_trades) + len(losing_trades)
        win_rate = len(winning_trades) / total_trades if total_trades > 0 else 0
        avg_win = np.mean([t['profit_loss_pct'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['profit_loss_pct'] for t in losing_trades]) if losing_trades else 0
        profit_factor = abs(sum(t['profit_loss'] for t in winning_trades) / sum(t['profit_loss'] for t in losing_trades)) if losing_trades and sum(t['profit_loss'] for t in losing_trades) != 0 else float('inf')

        # Signal analysis
        signal_accuracy = self.analyze_signal_accuracy(signal_history, winning_trades, losing_trades)

        return {
            'performance_metrics': {
                'initial_capital': initial_capital,
                'final_value': final_value,
                'total_return': total_return,
                'annualized_return': annualized_return,
                'volatility': volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'trading_days': trading_days
            },
            'trading_statistics': {
                'total_trades': total_trades,
                'winning_trades': len(winning_trades),
                'losing_trades': len(losing_trades),
                'win_rate': win_rate,
                'avg_win_pct': avg_win,
                'avg_loss_pct': avg_loss,
                'profit_factor': profit_factor,
                'avg_holding_days': np.mean([t['holding_days'] for t in winning_trades + losing_trades]) if total_trades > 0 else 0
            },
            'signal_analysis': signal_accuracy,
            'trade_details': {
                'winning_trades': winning_trades,
                'losing_trades': losing_trades,
                'all_trades': trades
            },
            'daily_values': daily_values
        }

    def analyze_signal_accuracy(self, signal_history, winning_trades, losing_trades):
        """Analyze accuracy of smart money signals"""
        signal_performance = {
            'Buy': {'wins': 0, 'losses': 0, 'total': 0},
            'Strong Buy': {'wins': 0, 'losses': 0, 'total': 0},
            'Sell': {'wins': 0, 'losses': 0, 'total': 0}
        }

        # Map trades back to signals
        for trade in winning_trades + losing_trades:
            # Find corresponding signal
            for signal in signal_history:
                if (signal['symbol'] == trade['symbol'] and
                    signal['date'] == trade['entry_date'] and
                    signal['signal'] in signal_performance):

                    signal_performance[signal['signal']]['total'] += 1
                    if trade in winning_trades:
                        signal_performance[signal['signal']]['wins'] += 1
                    else:
                        signal_performance[signal['signal']]['losses'] += 1
                    break

        # Calculate accuracy rates
        signal_accuracy = {}
        for signal_type, stats in signal_performance.items():
            if stats['total'] > 0:
                accuracy = stats['wins'] / stats['total']
                signal_accuracy[signal_type] = {
                    'accuracy': accuracy,
                    'total_trades': stats['total'],
                    'wins': stats['wins'],
                    'losses': stats['losses']
                }

        return signal_accuracy

def main():
    """Test backtesting framework"""
    print("Vietnam Stock Analysis - Strategy Backtesting Framework")
    print("=" * 70)

    backtester = VietnameseBacktester()

    try:
        # Test with key stocks over recent period
        symbols = ['VCB', 'HPG', 'VHM', 'CTG', 'BID']
        start_date = '2025-07-01'
        end_date = '2025-09-17'

        print(f"Testing backtest with {len(symbols)} stocks...")

        results = backtester.run_backtest(symbols, start_date, end_date)

        if 'error' in results:
            print(f"❌ Backtest error: {results['error']}")
            return

        # Display results
        perf = results['performance_metrics']
        trade_stats = results['trading_statistics']

        print(f"\n📊 Performance Results:")
        print(f"  Initial Capital: {perf['initial_capital']:,.0f} VND")
        print(f"  Final Value: {perf['final_value']:,.0f} VND")
        print(f"  Total Return: {perf['total_return']:.1%}")
        print(f"  Annualized Return: {perf['annualized_return']:.1%}")
        print(f"  Volatility: {perf['volatility']:.1%}")
        print(f"  Sharpe Ratio: {perf['sharpe_ratio']:.2f}")
        print(f"  Max Drawdown: {perf['max_drawdown']:.1%}")

        print(f"\n📈 Trading Statistics:")
        print(f"  Total Trades: {trade_stats['total_trades']}")
        print(f"  Win Rate: {trade_stats['win_rate']:.1%}")
        print(f"  Avg Win: {trade_stats['avg_win_pct']:.1%}")
        print(f"  Avg Loss: {trade_stats['avg_loss_pct']:.1%}")
        print(f"  Profit Factor: {trade_stats['profit_factor']:.2f}")
        print(f"  Avg Holding: {trade_stats['avg_holding_days']:.1f} days")

        print(f"\n🧠 Signal Accuracy:")
        for signal_type, accuracy_data in results['signal_analysis'].items():
            print(f"  {signal_type}: {accuracy_data['accuracy']:.1%} ({accuracy_data['wins']}/{accuracy_data['total_trades']})")

        # Overall assessment
        print(f"\n🎯 Strategy Assessment:")
        if perf['sharpe_ratio'] > 1.5:
            print("  ✅ EXCELLENT: High risk-adjusted returns")
        elif perf['sharpe_ratio'] > 1.0:
            print("  ✅ GOOD: Solid risk-adjusted performance")
        elif perf['sharpe_ratio'] > 0.5:
            print("  ⚠️ FAIR: Moderate performance")
        else:
            print("  ❌ POOR: Underperforming strategy")

        print(f"\n✅ Backtesting completed successfully!")

    except Exception as e:
        print(f"❌ Backtesting error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()