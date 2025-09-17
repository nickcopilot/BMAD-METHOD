#!/usr/bin/env python3
"""
Portfolio Optimization Engine
Modern Portfolio Theory implementation adapted for Vietnamese market constraints
"""

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from datetime import datetime, timedelta
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.models.database import get_db
from shared.analysis.smart_money import SmartMoneyAnalyzer

class VietnamesePortfolioOptimizer:
    """Portfolio optimizer with Vietnamese market-specific constraints"""

    def __init__(self):
        self.db = get_db()
        self.analyzer = SmartMoneyAnalyzer()

        # Vietnamese market constraints
        self.constraints = {
            'max_position_size': 0.15,        # Max 15% in any single stock
            'max_sector_allocation': 0.40,    # Max 40% in any sector
            'min_diversification': 8,         # Minimum 8 stocks in portfolio
            'max_stocks': 15,                 # Maximum 15 stocks (liquidity constraints)
            'transaction_cost': 0.0015,       # 0.15% transaction cost
            'min_position_size': 0.02,        # Minimum 2% position
            'cash_reserve': 0.05              # 5% cash reserve requirement
        }

        # Risk parameters for Vietnamese market
        self.risk_params = {
            'risk_free_rate': 0.06,           # Vietnamese government bonds
            'market_volatility_target': 0.20, # 20% annual volatility target
            'correlation_decay': 0.94,        # Weekly correlation decay
            'volatility_lookback': 60,        # 60-day volatility calculation
            'max_portfolio_beta': 1.3         # Maximum portfolio beta
        }

    def get_price_data(self, symbols, days_back=90):
        """Get price data for portfolio optimization"""
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

        return pd.DataFrame(price_data).sort_index()

    def calculate_returns(self, price_data):
        """Calculate daily returns matrix"""
        returns = price_data.pct_change().dropna()
        return returns

    def calculate_smart_money_scores(self, symbols):
        """Get smart money scores for portfolio construction"""
        scores = {}

        for symbol in symbols:
            try:
                analysis = self.analyzer.analyze_symbol(symbol, days_back=60)
                if 'error' not in analysis:
                    scores[symbol] = {
                        'score': analysis['market_context']['adjusted_score'],
                        'signal': analysis['composite_score']['signal_class'],
                        'momentum': analysis['composite_score']['component_scores']['momentum'],
                        'quality': analysis['composite_score']['component_scores']['accumulation']
                    }
                else:
                    scores[symbol] = {'score': 50, 'signal': 'Hold', 'momentum': 50, 'quality': 50}
            except:
                scores[symbol] = {'score': 50, 'signal': 'Hold', 'momentum': 50, 'quality': 50}

        return scores

    def get_sector_allocations(self, symbols):
        """Get sector information for portfolio constraints"""
        sector_map = {}

        stocks = self.db.get_all_stocks()
        for stock in stocks:
            if stock['symbol'] in symbols:
                sector_map[stock['symbol']] = stock['sector']

        return sector_map

    def calculate_covariance_matrix(self, returns):
        """Calculate covariance matrix with Vietnamese market adjustments"""
        # Basic covariance
        cov_matrix = returns.cov() * 252  # Annualize

        # Apply Vietnamese market volatility adjustment
        vol_adjustment = 1.2  # Vietnamese market typically 20% more volatile
        cov_matrix *= vol_adjustment

        return cov_matrix

    def objective_function(self, weights, returns, cov_matrix, smart_scores, symbols):
        """Multi-objective function: maximize return, minimize risk, incorporate smart money"""
        portfolio_return = np.dot(weights, returns.mean() * 252)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)

        # Smart money score adjustment
        smart_money_bonus = 0
        for i, symbol in enumerate(symbols):
            score_normalized = (smart_scores[symbol]['score'] - 50) / 50  # Convert to -1 to 1
            smart_money_bonus += weights[i] * score_normalized * 0.05  # 5% bonus for good signals

        # Risk-adjusted return with smart money overlay
        if portfolio_volatility > 0:
            sharpe_ratio = (portfolio_return - self.risk_params['risk_free_rate']) / portfolio_volatility
            objective = -(sharpe_ratio + smart_money_bonus)  # Negative for minimization
        else:
            objective = 1000  # Penalty for zero volatility

        return objective

    def create_constraints(self, symbols, sector_map, smart_scores):
        """Create optimization constraints for Vietnamese market"""
        n_assets = len(symbols)
        constraints = []

        # Weights sum to (1 - cash_reserve)
        investable_amount = 1 - self.constraints['cash_reserve']
        constraints.append({
            'type': 'eq',
            'fun': lambda x: np.sum(x) - investable_amount
        })

        # Maximum position size constraint
        for i in range(n_assets):
            constraints.append({
                'type': 'ineq',
                'fun': lambda x, i=i: self.constraints['max_position_size'] - x[i]
            })

        # Sector allocation constraints
        sectors = set(sector_map.values())
        for sector in sectors:
            sector_indices = [i for i, symbol in enumerate(symbols) if sector_map[symbol] == sector]
            if sector_indices:
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, indices=sector_indices: self.constraints['max_sector_allocation'] - sum(x[i] for i in indices)
                })

        # Minimum diversification (at least min_diversification non-zero positions)
        def min_diversification_constraint(x):
            non_zero_positions = sum(1 for weight in x if weight >= self.constraints['min_position_size'])
            return non_zero_positions - self.constraints['min_diversification']

        constraints.append({
            'type': 'ineq',
            'fun': min_diversification_constraint
        })

        # Smart money signal constraints (avoid weak signals in large positions)
        for i, symbol in enumerate(symbols):
            if smart_scores[symbol]['score'] < 45:  # Weak signals
                constraints.append({
                    'type': 'ineq',
                    'fun': lambda x, i=i: 0.08 - x[i]  # Max 8% for weak signals
                })

        return constraints

    def optimize_portfolio(self, symbols=None, target_return=None):
        """Optimize portfolio allocation using MPT with Vietnamese constraints"""
        if symbols is None:
            # Get all available stocks
            stocks = self.db.get_all_stocks()
            symbols = [stock['symbol'] for stock in stocks]

        # Limit to max_stocks for liquidity
        if len(symbols) > self.constraints['max_stocks']:
            # Prioritize by smart money scores
            smart_scores = self.calculate_smart_money_scores(symbols)
            symbols = sorted(symbols, key=lambda x: smart_scores[x]['score'], reverse=True)[:self.constraints['max_stocks']]

        print(f"Optimizing portfolio for {len(symbols)} stocks: {symbols}")

        # Get data
        price_data = self.get_price_data(symbols, days_back=90)
        returns = self.calculate_returns(price_data)
        cov_matrix = self.calculate_covariance_matrix(returns)
        smart_scores = self.calculate_smart_money_scores(symbols)
        sector_map = self.get_sector_allocations(symbols)

        # Setup optimization
        n_assets = len(symbols)
        initial_weights = np.array([1.0/n_assets] * n_assets) * (1 - self.constraints['cash_reserve'])

        # Bounds: min_position_size to max_position_size for each asset
        bounds = [(0, self.constraints['max_position_size']) for _ in range(n_assets)]

        # Constraints
        constraints = self.create_constraints(symbols, sector_map, smart_scores)

        # Optimize
        try:
            result = minimize(
                self.objective_function,
                initial_weights,
                args=(returns, cov_matrix, smart_scores, symbols),
                method='SLSQP',
                bounds=bounds,
                constraints=constraints,
                options={'maxiter': 1000, 'ftol': 1e-9}
            )

            if result.success:
                optimal_weights = result.x

                # Clean up small positions
                for i, weight in enumerate(optimal_weights):
                    if weight < self.constraints['min_position_size']:
                        optimal_weights[i] = 0

                # Renormalize
                total_weight = np.sum(optimal_weights)
                if total_weight > 0:
                    optimal_weights = optimal_weights / total_weight * (1 - self.constraints['cash_reserve'])

                return self.create_portfolio_report(symbols, optimal_weights, returns, cov_matrix, smart_scores, sector_map)

            else:
                raise Exception(f"Optimization failed: {result.message}")

        except Exception as e:
            print(f"Portfolio optimization error: {e}")
            return self.create_equal_weight_portfolio(symbols, smart_scores, sector_map)

    def create_portfolio_report(self, symbols, weights, returns, cov_matrix, smart_scores, sector_map):
        """Create comprehensive portfolio analysis report"""
        portfolio_return = np.dot(weights, returns.mean() * 252)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_volatility = np.sqrt(portfolio_variance)
        sharpe_ratio = (portfolio_return - self.risk_params['risk_free_rate']) / portfolio_volatility if portfolio_volatility > 0 else 0

        # Portfolio composition
        positions = []
        sector_allocations = {}

        for i, symbol in enumerate(symbols):
            if weights[i] > 0.001:  # Only include meaningful positions
                sector = sector_map.get(symbol, 'Unknown')

                positions.append({
                    'symbol': symbol,
                    'weight': weights[i],
                    'weight_pct': weights[i] * 100,
                    'sector': sector,
                    'smart_score': smart_scores[symbol]['score'],
                    'signal': smart_scores[symbol]['signal'],
                    'expected_return': returns[symbol].mean() * 252 if symbol in returns.columns else 0,
                    'volatility': returns[symbol].std() * np.sqrt(252) if symbol in returns.columns else 0
                })

                # Sector allocation
                if sector not in sector_allocations:
                    sector_allocations[sector] = 0
                sector_allocations[sector] += weights[i]

        # Sort positions by weight
        positions.sort(key=lambda x: x['weight'], reverse=True)

        # Risk metrics
        cash_allocation = self.constraints['cash_reserve']

        report = {
            'portfolio_metrics': {
                'expected_return': portfolio_return,
                'volatility': portfolio_volatility,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown_estimate': portfolio_volatility * 2,  # Rough estimate
                'cash_allocation': cash_allocation,
                'number_of_positions': len([p for p in positions if p['weight'] > 0.01])
            },
            'positions': positions,
            'sector_allocations': sector_allocations,
            'risk_analysis': self.calculate_risk_metrics(weights, returns, cov_matrix),
            'smart_money_analysis': self.analyze_smart_money_allocation(positions)
        }

        return report

    def create_equal_weight_portfolio(self, symbols, smart_scores, sector_map):
        """Fallback equal-weight portfolio with smart money filtering"""
        # Filter for decent smart money scores
        good_symbols = [s for s in symbols if smart_scores[s]['score'] >= 50]

        if len(good_symbols) < 8:
            good_symbols = symbols[:8]  # Take top stocks if not enough good signals

        weight_per_stock = (1 - self.constraints['cash_reserve']) / len(good_symbols)
        weights = np.array([weight_per_stock if symbol in good_symbols else 0 for symbol in symbols])

        # Get price data for return calculation
        price_data = self.get_price_data(symbols, days_back=90)
        returns = self.calculate_returns(price_data)
        cov_matrix = self.calculate_covariance_matrix(returns)

        return self.create_portfolio_report(symbols, weights, returns, cov_matrix, smart_scores, sector_map)

    def calculate_risk_metrics(self, weights, returns, cov_matrix):
        """Calculate comprehensive risk metrics"""
        # VaR calculation (95% confidence)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        var_95 = 1.645 * portfolio_std  # Daily 95% VaR

        # Expected Shortfall (CVaR)
        cvar_95 = var_95 * 1.28  # Approximation for normal distribution

        # Maximum theoretical loss
        max_loss = portfolio_std * 3  # 3-sigma event

        return {
            'daily_var_95': var_95,
            'daily_cvar_95': cvar_95,
            'annual_volatility': portfolio_std,
            'max_theoretical_loss': max_loss,
            'risk_budget_utilization': portfolio_std / self.risk_params['market_volatility_target']
        }

    def analyze_smart_money_allocation(self, positions):
        """Analyze smart money signal distribution in portfolio"""
        total_weight = sum(p['weight'] for p in positions)

        signal_allocation = {}
        score_weighted_average = 0

        for position in positions:
            signal = position['signal']
            if signal not in signal_allocation:
                signal_allocation[signal] = 0
            signal_allocation[signal] += position['weight']

            score_weighted_average += position['smart_score'] * position['weight']

        if total_weight > 0:
            score_weighted_average /= total_weight

        return {
            'signal_allocation': signal_allocation,
            'weighted_average_score': score_weighted_average,
            'strong_signal_allocation': signal_allocation.get('Buy', 0) + signal_allocation.get('Strong Buy', 0),
            'weak_signal_allocation': signal_allocation.get('Sell', 0) + signal_allocation.get('Strong Sell', 0)
        }

def main():
    """Test portfolio optimization"""
    print("Vietnam Stock Analysis - Portfolio Optimization Engine")
    print("=" * 70)

    optimizer = VietnamesePortfolioOptimizer()

    try:
        print("Optimizing portfolio with Vietnamese market constraints...")
        portfolio = optimizer.optimize_portfolio()

        print(f"\n📊 Portfolio Optimization Results:")
        metrics = portfolio['portfolio_metrics']
        print(f"  Expected Return: {metrics['expected_return']:.1%}")
        print(f"  Volatility: {metrics['volatility']:.1%}")
        print(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"  Cash Reserve: {metrics['cash_allocation']:.1%}")
        print(f"  Number of Positions: {metrics['number_of_positions']}")

        print(f"\n🏆 Top Holdings:")
        for i, position in enumerate(portfolio['positions'][:5], 1):
            print(f"  {i}. {position['symbol']}: {position['weight_pct']:.1f}% ({position['signal']}, {position['smart_score']:.1f})")

        print(f"\n🏢 Sector Allocation:")
        for sector, allocation in sorted(portfolio['sector_allocations'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {sector.replace('_', ' ').title()}: {allocation:.1%}")

        print(f"\n⚠️ Risk Analysis:")
        risk = portfolio['risk_analysis']
        print(f"  Daily VaR (95%): {risk['daily_var_95']:.1%}")
        print(f"  Annual Volatility: {risk['annual_volatility']:.1%}")
        print(f"  Risk Budget Used: {risk['risk_budget_utilization']:.1%}")

        print(f"\n🧠 Smart Money Analysis:")
        smart = portfolio['smart_money_analysis']
        print(f"  Portfolio Score: {smart['weighted_average_score']:.1f}")
        print(f"  Strong Signals: {smart['strong_signal_allocation']:.1%}")

        print(f"\n✅ Portfolio optimization completed successfully!")

    except Exception as e:
        print(f"❌ Portfolio optimization error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()