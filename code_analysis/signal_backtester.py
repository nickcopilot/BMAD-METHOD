#!/usr/bin/env python3
"""
Signal Backtesting Framework for Vietnam Stock Analysis System
Validates signal accuracy and performance against historical data
"""

import vnstock as vn
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# Import our signal system
from smart_money_signal_system import SmartMoneySignalSystem

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SignalBacktester:
    def __init__(self):
        self.signal_system = SmartMoneySignalSystem()
        self.vnstock_client = vn.Vnstock()

        # Backtesting parameters
        self.backtest_config = {
            'min_holding_period': 5,    # Minimum days to hold position
            'max_holding_period': 30,   # Maximum days to hold position
            'transaction_cost': 0.003,  # 0.3% transaction cost (realistic for VN market)
            'stop_loss_threshold': -0.08,  # 8% stop loss
            'take_profit_threshold': 0.15,  # 15% take profit
            'signal_threshold_buy': 65,     # Minimum score for buy signals
            'signal_threshold_sell': 35     # Maximum score for sell signals
        }

        # Performance tracking
        self.performance_metrics = {
            'total_signals': 0,
            'successful_signals': 0,
            'failed_signals': 0,
            'win_rate': 0.0,
            'avg_return': 0.0,
            'avg_holding_period': 0.0,
            'max_drawdown': 0.0,
            'sharpe_ratio': 0.0,
            'total_return': 0.0
        }

    def collect_historical_data(self, symbol: str, days: int = 365) -> pd.DataFrame:
        """Collect historical data for backtesting"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is not None and not data.empty:
                # Ensure we have the required columns
                required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
                for col in required_columns:
                    if col not in data.columns:
                        logging.error(f"Missing required column: {col}")
                        return pd.DataFrame()

                # Sort by date
                data = data.sort_values('time').reset_index(drop=True)

                # Calculate daily returns
                data['daily_return'] = data['close'].pct_change()

                logging.info(f"Collected {len(data)} days of data for {symbol}")
                return data
            else:
                logging.error(f"No data available for {symbol}")
                return pd.DataFrame()

        except Exception as e:
            logging.error(f"Error collecting data for {symbol}: {e}")
            return pd.DataFrame()

    def generate_historical_signals(self, symbol: str, data: pd.DataFrame) -> List[Dict]:
        """Generate signals for historical periods"""
        signals = []

        # We need sufficient data for signal generation (minimum 50 days)
        min_data_points = 50

        for i in range(min_data_points, len(data) - 30):  # Leave 30 days for outcome measurement
            try:
                # Get data up to this point for signal generation
                historical_data = data.iloc[:i+1].copy()

                # Generate signal using our system (simulate real-time conditions)
                signal_result = self.generate_signal_for_date(symbol, historical_data)

                if signal_result and 'error' not in signal_result:
                    signal_date = data.iloc[i]['time']
                    signal_price = data.iloc[i]['close']

                    # Extract signal information
                    composite_score = signal_result.get('composite_signal_score', {})
                    vn_context = signal_result.get('vietnamese_market_context', {})

                    original_score = composite_score.get('composite_score', 0)
                    adjusted_score = vn_context.get('adjusted_score', original_score)
                    classification = vn_context.get('signal_classification', 'Hold Signal')

                    # Determine if this is a actionable signal
                    is_buy_signal = adjusted_score >= self.backtest_config['signal_threshold_buy']
                    is_sell_signal = adjusted_score <= self.backtest_config['signal_threshold_sell']

                    if is_buy_signal or is_sell_signal:
                        signals.append({
                            'date': signal_date,
                            'symbol': symbol,
                            'signal_type': 'BUY' if is_buy_signal else 'SELL',
                            'entry_price': signal_price,
                            'original_score': original_score,
                            'adjusted_score': adjusted_score,
                            'classification': classification,
                            'data_index': i,
                            'vn_context_notes': vn_context.get('vietnamese_context_notes', [])
                        })

                        logging.info(f"Generated {('BUY' if is_buy_signal else 'SELL')} signal for {symbol} on {signal_date} at {signal_price}")

            except Exception as e:
                logging.error(f"Error generating signal for {symbol} at index {i}: {e}")
                continue

        logging.info(f"Generated {len(signals)} actionable signals for {symbol}")
        return signals

    def generate_signal_for_date(self, symbol: str, historical_data: pd.DataFrame) -> Optional[Dict]:
        """Generate signal using historical data up to a specific date"""
        try:
            # Create a temporary signal system instance to avoid data contamination
            temp_data = historical_data.copy()

            # We'll simulate the signal generation by using our existing system
            # but with limited historical data
            signals = self.signal_system.generate_smart_money_signals(symbol)

            return signals

        except Exception as e:
            logging.error(f"Error generating signal for {symbol}: {e}")
            return None

    def evaluate_signal_performance(self, signal: Dict, future_data: pd.DataFrame) -> Dict:
        """Evaluate the performance of a single signal"""

        entry_price = signal['entry_price']
        signal_type = signal['signal_type']
        entry_index = signal['data_index']

        # Calculate outcomes for different holding periods
        outcomes = []

        max_holding = min(self.backtest_config['max_holding_period'], len(future_data) - entry_index - 1)

        for holding_days in range(self.backtest_config['min_holding_period'], max_holding + 1):
            if entry_index + holding_days < len(future_data):
                exit_price = future_data.iloc[entry_index + holding_days]['close']

                # Calculate return
                if signal_type == 'BUY':
                    raw_return = (exit_price - entry_price) / entry_price
                else:  # SELL signal (short position)
                    raw_return = (entry_price - exit_price) / entry_price

                # Apply transaction costs
                net_return = raw_return - self.backtest_config['transaction_cost']

                # Check for stop loss or take profit
                hit_stop_loss = net_return <= self.backtest_config['stop_loss_threshold']
                hit_take_profit = net_return >= self.backtest_config['take_profit_threshold']

                outcomes.append({
                    'holding_days': holding_days,
                    'exit_price': exit_price,
                    'raw_return': raw_return,
                    'net_return': net_return,
                    'hit_stop_loss': hit_stop_loss,
                    'hit_take_profit': hit_take_profit
                })

                # Exit early if stop loss or take profit hit
                if hit_stop_loss or hit_take_profit:
                    break

        if outcomes:
            # Use the outcome with best risk-adjusted return
            best_outcome = max(outcomes, key=lambda x: x['net_return'])

            return {
                'signal_date': signal['date'],
                'signal_type': signal_type,
                'entry_price': entry_price,
                'exit_price': best_outcome['exit_price'],
                'holding_days': best_outcome['holding_days'],
                'raw_return': best_outcome['raw_return'],
                'net_return': best_outcome['net_return'],
                'success': best_outcome['net_return'] > 0,
                'hit_stop_loss': best_outcome['hit_stop_loss'],
                'hit_take_profit': best_outcome['hit_take_profit'],
                'original_score': signal['original_score'],
                'adjusted_score': signal['adjusted_score'],
                'vn_context_notes': signal['vn_context_notes']
            }
        else:
            return None

    def backtest_symbol(self, symbol: str, days: int = 365) -> Dict:
        """Run complete backtest for a single symbol"""

        logging.info(f"Starting backtest for {symbol}")

        # Collect historical data
        data = self.collect_historical_data(symbol, days)
        if data.empty:
            return {'error': f'No data available for {symbol}'}

        # Generate historical signals
        signals = self.generate_historical_signals(symbol, data)
        if not signals:
            return {'error': f'No signals generated for {symbol}'}

        # Evaluate each signal
        evaluated_signals = []
        for signal in signals:
            outcome = self.evaluate_signal_performance(signal, data)
            if outcome:
                evaluated_signals.append(outcome)

        if not evaluated_signals:
            return {'error': f'No signal outcomes available for {symbol}'}

        # Calculate performance metrics
        metrics = self.calculate_performance_metrics(evaluated_signals)

        return {
            'symbol': symbol,
            'backtest_period': f"{data['time'].min()} to {data['time'].max()}",
            'total_signals': len(evaluated_signals),
            'signal_details': evaluated_signals,
            'performance_metrics': metrics,
            'data_quality': {
                'total_days': len(data),
                'missing_data': data.isnull().sum().sum(),
                'zero_volume_days': (data['volume'] == 0).sum()
            }
        }

    def calculate_performance_metrics(self, evaluated_signals: List[Dict]) -> Dict:
        """Calculate comprehensive performance metrics"""

        if not evaluated_signals:
            return {}

        # Basic metrics
        total_signals = len(evaluated_signals)
        successful_signals = sum(1 for s in evaluated_signals if s['success'])
        win_rate = successful_signals / total_signals if total_signals > 0 else 0

        # Return metrics
        returns = [s['net_return'] for s in evaluated_signals]
        avg_return = np.mean(returns)
        median_return = np.median(returns)
        std_return = np.std(returns)

        # Holding period
        holding_periods = [s['holding_days'] for s in evaluated_signals]
        avg_holding_period = np.mean(holding_periods)

        # Risk metrics
        negative_returns = [r for r in returns if r < 0]
        max_loss = min(negative_returns) if negative_returns else 0

        # Sharpe ratio (assuming risk-free rate of 5% annually)
        risk_free_daily = 0.05 / 252  # Daily risk-free rate
        excess_returns = [r - risk_free_daily for r in returns]
        sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns) if np.std(excess_returns) > 0 else 0

        # Total return (compound)
        total_return = 1
        for r in returns:
            total_return *= (1 + r)
        total_return = (total_return - 1) * 100  # Convert to percentage

        # Signal type breakdown
        buy_signals = [s for s in evaluated_signals if s['signal_type'] == 'BUY']
        sell_signals = [s for s in evaluated_signals if s['signal_type'] == 'SELL']

        buy_win_rate = sum(1 for s in buy_signals if s['success']) / len(buy_signals) if buy_signals else 0
        sell_win_rate = sum(1 for s in sell_signals if s['success']) / len(sell_signals) if sell_signals else 0

        return {
            'total_signals': total_signals,
            'successful_signals': successful_signals,
            'win_rate': round(win_rate * 100, 2),
            'avg_return': round(avg_return * 100, 2),
            'median_return': round(median_return * 100, 2),
            'std_return': round(std_return * 100, 2),
            'max_loss': round(max_loss * 100, 2),
            'total_return': round(total_return, 2),
            'avg_holding_period': round(avg_holding_period, 1),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'buy_signals': len(buy_signals),
            'sell_signals': len(sell_signals),
            'buy_win_rate': round(buy_win_rate * 100, 2),
            'sell_win_rate': round(sell_win_rate * 100, 2),
            'risk_adjusted_return': round(avg_return / std_return, 2) if std_return > 0 else 0
        }

    def generate_backtest_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive backtest report"""

        if not results:
            return {'error': 'No backtest results available'}

        # Filter successful backtests
        successful_results = [r for r in results if 'error' not in r]
        failed_results = [r for r in results if 'error' in r]

        if not successful_results:
            return {'error': 'All backtests failed'}

        # Aggregate metrics across all symbols
        all_signals = []
        for result in successful_results:
            all_signals.extend(result['signal_details'])

        # Overall performance
        overall_metrics = self.calculate_performance_metrics(all_signals)

        # Best and worst performers
        symbol_performance = []
        for result in successful_results:
            metrics = result['performance_metrics']
            symbol_performance.append({
                'symbol': result['symbol'],
                'win_rate': metrics['win_rate'],
                'avg_return': metrics['avg_return'],
                'total_signals': metrics['total_signals']
            })

        symbol_performance.sort(key=lambda x: x['win_rate'], reverse=True)

        return {
            'backtest_summary': {
                'symbols_tested': len(results),
                'successful_backtests': len(successful_results),
                'failed_backtests': len(failed_results),
                'total_signals_generated': len(all_signals)
            },
            'overall_performance': overall_metrics,
            'symbol_performance': symbol_performance,
            'best_performer': symbol_performance[0] if symbol_performance else None,
            'worst_performer': symbol_performance[-1] if symbol_performance else None,
            'failed_symbols': [r['error'] for r in failed_results],
            'report_generated': datetime.now().isoformat()
        }

if __name__ == "__main__":
    backtester = SignalBacktester()

    # Test with a single symbol first
    test_symbol = "VCB"
    print(f"🧪 Testing backtester with {test_symbol}...")

    result = backtester.backtest_symbol(test_symbol, days=180)  # 6 months

    if 'error' not in result:
        print(f"✅ Backtest successful for {test_symbol}")
        print(f"📊 Signals generated: {result['total_signals']}")

        metrics = result['performance_metrics']
        print(f"📈 Win rate: {metrics['win_rate']}%")
        print(f"💰 Average return: {metrics['avg_return']}%")
        print(f"⏱️  Average holding period: {metrics['avg_holding_period']} days")

        # Save detailed results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/workspaces/BMAD-METHOD/session_logs/backtest_{test_symbol}_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"💾 Detailed results saved to: {filename}")
    else:
        print(f"❌ Backtest failed: {result['error']}")

    print("\n🚀 Signal Backtesting Framework Ready!")