#!/usr/bin/env python3
"""
Comprehensive Stock Report Generator
Combines all analysis systems to provide deep insights on Vietnamese stocks
including company operations, technical analysis, and smart money tracking
"""

import vnstock as vn
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Tuple
import os
import sys

# Import our custom analyzers
from advanced_stock_analyzer import AdvancedStockAnalyzer
from eic_framework import EICFramework
from market_maker_analyzer import MarketMakerAnalyzer
from stock_universe_manager import VietnamStockUniverse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ComprehensiveStockReporter:
    def __init__(self):
        self.vnstock_client = vn.Vnstock()

        # Initialize all analyzers
        self.advanced_analyzer = AdvancedStockAnalyzer()
        self.eic_framework = EICFramework()
        self.mm_analyzer = MarketMakerAnalyzer()
        self.universe_manager = VietnamStockUniverse()

        # Report templates and scoring
        self.report_weights = {
            'technical_analysis': 0.25,
            'eic_analysis': 0.30,
            'market_maker_analysis': 0.25,
            'fundamental_proxy': 0.20
        }

        # Company operation indicators (proxies based on available data)
        self.operation_indicators = {
            'efficiency_metrics': ['revenue_growth_proxy', 'margin_stability', 'asset_turnover_proxy'],
            'growth_metrics': ['price_momentum', 'volume_growth', 'market_expansion'],
            'stability_metrics': ['earnings_consistency_proxy', 'dividend_reliability', 'balance_sheet_strength'],
            'competitive_metrics': ['market_share_proxy', 'pricing_power', 'innovation_capability']
        }

    def generate_comprehensive_report(self, symbol: str, sector: str = None) -> Dict:
        """Generate a comprehensive report combining all analysis systems"""

        logging.info(f"Generating comprehensive report for {symbol}")

        if not sector:
            sector = self.universe_manager.classify_stock_sector(symbol)

        report = {
            'symbol': symbol,
            'sector': sector,
            'report_date': datetime.now().isoformat(),
            'report_type': 'comprehensive_analysis'
        }

        try:
            # 1. Technical Analysis
            logging.info("Running technical analysis...")
            technical_analysis = self.advanced_analyzer.generate_comprehensive_analysis(symbol)

            # 2. EIC Framework Analysis
            logging.info("Running EIC framework analysis...")
            eic_analysis = self.eic_framework.calculate_comprehensive_eic_score(symbol, sector)

            # 3. Market Maker Analysis
            logging.info("Running market maker analysis...")
            mm_analysis = self.mm_analyzer.analyze_market_maker_style(symbol)

            # 4. Company Operations Analysis (Proxy)
            logging.info("Analyzing company operations...")
            operations_analysis = self.analyze_company_operations(symbol, sector)

            # 5. Smart Money Tracking
            logging.info("Tracking smart money indicators...")
            smart_money_tracking = self.track_smart_money_comprehensive(symbol)

            # 6. Entry/Exit Signal Generation
            logging.info("Generating trading signals...")
            trading_signals = self.generate_advanced_trading_signals(
                technical_analysis, eic_analysis, mm_analysis, operations_analysis
            )

            # Compile all analyses
            report.update({
                'technical_analysis': technical_analysis,
                'eic_analysis': eic_analysis,
                'market_maker_analysis': mm_analysis,
                'company_operations': operations_analysis,
                'smart_money_tracking': smart_money_tracking,
                'trading_signals': trading_signals,
                'composite_score': self.calculate_composite_score(
                    technical_analysis, eic_analysis, mm_analysis, operations_analysis
                ),
                'executive_summary': self.generate_executive_summary(
                    symbol, sector, technical_analysis, eic_analysis, mm_analysis, operations_analysis
                ),
                'risk_assessment': self.comprehensive_risk_assessment(
                    technical_analysis, eic_analysis, mm_analysis
                ),
                'time_sensitive_factors': self.identify_time_sensitive_factors(
                    mm_analysis, trading_signals
                )
            })

            return report

        except Exception as e:
            logging.error(f"Error generating comprehensive report for {symbol}: {e}")
            report['error'] = str(e)
            return report

    def analyze_company_operations(self, symbol: str, sector: str) -> Dict:
        """Analyze company operations using available market data as proxies"""

        try:
            # Get extended data for operational analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 1 year

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'error': 'No data available'}

            operations_score = 50  # Base score
            metrics = {}

            # 1. Revenue Growth Proxy (Price * Volume trend)
            data['revenue_proxy'] = data['close'] * data['volume']
            revenue_growth = self.calculate_growth_trend(data['revenue_proxy'])

            metrics['revenue_growth_proxy'] = {
                'annual_growth_rate': revenue_growth * 100,
                'trend': 'Growing' if revenue_growth > 0.05 else 'Stable' if revenue_growth > -0.05 else 'Declining',
                'score': max(0, min(100, 50 + revenue_growth * 200))
            }
            operations_score += (metrics['revenue_growth_proxy']['score'] - 50) * 0.25

            # 2. Operational Efficiency (Price stability with volume growth)
            price_volatility = data['close'].pct_change().std() * np.sqrt(252)
            volume_growth = self.calculate_growth_trend(data['volume'])

            efficiency_score = max(0, min(100, 100 - price_volatility * 100 + volume_growth * 50))

            metrics['operational_efficiency'] = {
                'price_volatility': price_volatility,
                'volume_growth': volume_growth,
                'efficiency_score': efficiency_score,
                'assessment': 'High' if efficiency_score > 70 else 'Medium' if efficiency_score > 50 else 'Low'
            }
            operations_score += (efficiency_score - 50) * 0.25

            # 3. Market Position Strength (Relative performance)
            vnindex = self.get_market_benchmark_data(start_date, end_date)
            if vnindex is not None:
                relative_performance = self.calculate_relative_performance(data, vnindex)

                metrics['market_position'] = {
                    'relative_performance': relative_performance * 100,
                    'market_outperformance': relative_performance > 0,
                    'position_strength': 'Strong' if relative_performance > 0.1 else 'Average' if relative_performance > -0.1 else 'Weak',
                    'score': max(0, min(100, 50 + relative_performance * 100))
                }
                operations_score += (metrics['market_position']['score'] - 50) * 0.25

            # 4. Business Stability (Consistent trading patterns)
            trading_consistency = self.assess_trading_consistency(data)

            metrics['business_stability'] = trading_consistency
            operations_score += (trading_consistency['score'] - 50) * 0.25

            # 5. Sector-Specific Operations Analysis
            sector_analysis = self.analyze_sector_specific_operations(symbol, sector, data)
            metrics['sector_specific'] = sector_analysis

            return {
                'symbol': symbol,
                'sector': sector,
                'operations_score': max(0, min(100, operations_score)),
                'operations_grade': self.grade_operations(operations_score),
                'key_metrics': metrics,
                'operational_strengths': self.identify_operational_strengths(metrics),
                'operational_challenges': self.identify_operational_challenges(metrics),
                'management_effectiveness': self.assess_management_effectiveness(metrics),
                'competitive_positioning': self.assess_competitive_positioning(metrics, sector),
                'growth_trajectory': self.assess_growth_trajectory(metrics),
                'commentary': self.generate_operations_commentary(metrics, operations_score)
            }

        except Exception as e:
            logging.error(f"Error analyzing company operations for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def track_smart_money_comprehensive(self, symbol: str) -> Dict:
        """Comprehensive smart money tracking with advanced indicators"""

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=90)  # 3 months for smart money tracking

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            if data is None or data.empty:
                return {'symbol': symbol, 'error': 'No data available'}

            smart_money_score = 50
            indicators = {}

            # 1. Advanced Volume Analysis
            volume_analysis = self.advanced_volume_analysis(data)
            indicators['volume_analysis'] = volume_analysis
            smart_money_score += (volume_analysis['score'] - 50) * 0.3

            # 2. Price Action Analysis
            price_action = self.analyze_smart_money_price_action(data)
            indicators['price_action'] = price_action
            smart_money_score += (price_action['score'] - 50) * 0.25

            # 3. Timing Analysis
            timing_analysis = self.analyze_smart_money_timing(data)
            indicators['timing_patterns'] = timing_analysis
            smart_money_score += (timing_analysis['score'] - 50) * 0.2

            # 4. Accumulation/Distribution Analysis
            accumulation_analysis = self.analyze_accumulation_distribution_advanced(data)
            indicators['accumulation_distribution'] = accumulation_analysis
            smart_money_score += (accumulation_analysis['score'] - 50) * 0.25

            # 5. Smart Money Flow Direction
            flow_direction = self.determine_smart_money_flow(indicators)

            return {
                'symbol': symbol,
                'smart_money_score': max(0, min(100, smart_money_score)),
                'flow_direction': flow_direction,
                'confidence_level': self.assess_smart_money_confidence(smart_money_score, indicators),
                'indicators': indicators,
                'key_signals': self.extract_key_smart_money_signals(indicators),
                'recommended_actions': self.recommend_smart_money_actions(smart_money_score, flow_direction),
                'monitoring_points': self.identify_smart_money_monitoring_points(indicators)
            }

        except Exception as e:
            logging.error(f"Error tracking smart money for {symbol}: {e}")
            return {'symbol': symbol, 'error': str(e)}

    def generate_advanced_trading_signals(self, technical: Dict, eic: Dict, mm: Dict, operations: Dict) -> Dict:
        """Generate advanced trading signals based on all analyses"""

        signals = {
            'primary_signals': [],
            'secondary_signals': [],
            'risk_signals': [],
            'entry_points': [],
            'exit_points': [],
            'position_sizing': {},
            'time_horizon': '',
            'overall_signal_strength': 0
        }

        signal_strength = 0

        # Technical signals
        if technical.get('executive_summary', {}).get('opportunity_score', 0) > 70:
            signals['primary_signals'].append({
                'source': 'technical',
                'signal': 'Strong technical setup',
                'strength': 'High'
            })
            signal_strength += 25

        # EIC signals
        eic_score = eic.get('eic_score', 50)
        if eic_score > 70:
            signals['primary_signals'].append({
                'source': 'eic',
                'signal': 'Favorable EIC environment',
                'strength': 'High'
            })
            signal_strength += 25

        # Market maker signals
        if mm.get('smart_money_analysis', {}).get('flow_direction') == 'Inflow':
            signals['primary_signals'].append({
                'source': 'market_maker',
                'signal': 'Smart money accumulation',
                'strength': 'Medium'
            })
            signal_strength += 20

        # Operations signals
        operations_score = operations.get('operations_score', 50)
        if operations_score > 65:
            signals['secondary_signals'].append({
                'source': 'operations',
                'signal': 'Strong operational metrics',
                'strength': 'Medium'
            })
            signal_strength += 15

        signals['overall_signal_strength'] = min(100, signal_strength)

        # Generate specific entry/exit points
        signals.update(self.generate_specific_trading_levels(technical, mm))

        return signals

    def calculate_composite_score(self, technical: Dict, eic: Dict, mm: Dict, operations: Dict) -> Dict:
        """Calculate composite investment score"""

        # Extract scores from each analysis
        technical_score = technical.get('executive_summary', {}).get('opportunity_score', 50)
        eic_score = eic.get('eic_score', 50)
        mm_score = mm.get('smart_money_analysis', {}).get('smart_money_score', 50)
        operations_score = operations.get('operations_score', 50)

        # Weighted composite score
        composite = (
            technical_score * self.report_weights['technical_analysis'] +
            eic_score * self.report_weights['eic_analysis'] +
            mm_score * self.report_weights['market_maker_analysis'] +
            operations_score * self.report_weights['fundamental_proxy']
        )

        return {
            'composite_score': composite,
            'investment_grade': self.determine_composite_grade(composite),
            'component_scores': {
                'technical': technical_score,
                'eic': eic_score,
                'market_maker': mm_score,
                'operations': operations_score
            },
            'weights_used': self.report_weights,
            'score_interpretation': self.interpret_composite_score(composite)
        }

    # Helper methods for detailed analysis

    def calculate_growth_trend(self, series: pd.Series) -> float:
        """Calculate growth trend over the series"""
        if len(series) < 30:
            return 0.0

        first_month = series.head(30).mean()
        last_month = series.tail(30).mean()

        if first_month == 0:
            return 0.0

        return (last_month / first_month) - 1

    def get_market_benchmark_data(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get VN-Index benchmark data"""
        try:
            vnindex = self.vnstock_client.stock(symbol='VNINDEX', source='VCI')
            return vnindex.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )
        except:
            return None

    def calculate_relative_performance(self, stock_data: pd.DataFrame, market_data: pd.DataFrame) -> float:
        """Calculate relative performance vs market"""
        if market_data is None or market_data.empty:
            return 0.0

        stock_return = (stock_data['close'].iloc[-1] / stock_data['close'].iloc[0]) - 1
        market_return = (market_data['close'].iloc[-1] / market_data['close'].iloc[0]) - 1

        return stock_return - market_return

    def assess_trading_consistency(self, data: pd.DataFrame) -> Dict:
        """Assess trading consistency as proxy for business stability"""

        # Volume consistency
        volume_cv = data['volume'].std() / data['volume'].mean()

        # Price range consistency
        daily_ranges = (data['high'] - data['low']) / data['close']
        range_cv = daily_ranges.std() / daily_ranges.mean()

        # Trading frequency (non-zero volume days)
        trading_days = len(data[data['volume'] > 0])
        trading_frequency = trading_days / len(data)

        consistency_score = max(0, min(100, 100 - volume_cv * 50 - range_cv * 30 + trading_frequency * 30))

        return {
            'volume_consistency': 1 - volume_cv,
            'price_range_consistency': 1 - range_cv,
            'trading_frequency': trading_frequency,
            'score': consistency_score,
            'assessment': 'High' if consistency_score > 70 else 'Medium' if consistency_score > 50 else 'Low'
        }

    def analyze_sector_specific_operations(self, symbol: str, sector: str, data: pd.DataFrame) -> Dict:
        """Sector-specific operational analysis"""

        sector_metrics = {
            'Banks': self.analyze_banking_operations(data),
            'Real_Estate': self.analyze_real_estate_operations(data),
            'Technology': self.analyze_technology_operations(data),
            'Manufacturing': self.analyze_manufacturing_operations(data)
        }

        return sector_metrics.get(sector, {'score': 50, 'analysis': 'Generic sector analysis'})

    def analyze_banking_operations(self, data: pd.DataFrame) -> Dict:
        """Banking sector specific analysis"""
        # Banks: focus on stability and consistency
        price_stability = 1 / (data['close'].pct_change().std() + 0.01)
        volume_growth = self.calculate_growth_trend(data['volume'])

        score = min(100, price_stability * 30 + max(0, volume_growth) * 70 + 40)

        return {
            'score': score,
            'price_stability': price_stability,
            'deposit_growth_proxy': volume_growth,
            'assessment': 'Banking operations appear stable' if score > 60 else 'Some operational concerns'
        }

    def analyze_real_estate_operations(self, data: pd.DataFrame) -> Dict:
        """Real estate sector specific analysis"""
        # Real estate: focus on cyclical patterns and volume
        seasonal_variance = data.groupby(data.index.month)['volume'].mean().std()
        avg_volume = data['volume'].mean()
        volume_trend = self.calculate_growth_trend(data['volume'])

        score = max(0, min(100, 50 + volume_trend * 100 - seasonal_variance / avg_volume * 50))

        return {
            'score': score,
            'seasonal_variance': seasonal_variance,
            'volume_trend': volume_trend,
            'assessment': 'Real estate operations showing growth' if score > 60 else 'Market challenges evident'
        }

    def analyze_technology_operations(self, data: pd.DataFrame) -> Dict:
        """Technology sector specific analysis"""
        # Technology: focus on growth and momentum
        momentum = data['close'].pct_change(20).iloc[-1] if len(data) > 20 else 0
        volume_acceleration = self.calculate_growth_trend(data['volume'].tail(60))

        score = min(100, max(0, 50 + momentum * 100 + volume_acceleration * 50))

        return {
            'score': score,
            'momentum': momentum,
            'volume_acceleration': volume_acceleration,
            'assessment': 'Technology operations expanding' if score > 65 else 'Growth challenges'
        }

    def analyze_manufacturing_operations(self, data: pd.DataFrame) -> Dict:
        """Manufacturing sector specific analysis"""
        # Manufacturing: focus on efficiency and consistency
        efficiency = data['volume'].mean() / data['close'].mean()  # Volume per price unit
        consistency = self.assess_trading_consistency(data)['score']

        score = (efficiency * 0.1 + consistency) / 1.1  # Normalize

        return {
            'score': min(100, score),
            'operational_efficiency': efficiency,
            'consistency_score': consistency,
            'assessment': 'Manufacturing operations efficient' if score > 60 else 'Efficiency concerns'
        }

    def advanced_volume_analysis(self, data: pd.DataFrame) -> Dict:
        """Advanced volume analysis for smart money detection"""

        # Volume distribution analysis
        volume_percentiles = data['volume'].quantile([0.5, 0.75, 0.9, 0.95])

        # Large block frequency
        large_blocks = len(data[data['volume'] > volume_percentiles[0.9]]) / len(data) * 100

        # Volume-price correlation
        volume_price_corr = data['volume'].corr(data['close'].pct_change().abs())

        score = min(100, large_blocks * 2 + max(0, volume_price_corr) * 50 + 30)

        return {
            'large_block_frequency': large_blocks,
            'volume_price_correlation': volume_price_corr,
            'volume_distribution': volume_percentiles.to_dict(),
            'score': score,
            'interpretation': 'High institutional activity' if score > 70 else 'Moderate activity'
        }

    def analyze_smart_money_price_action(self, data: pd.DataFrame) -> Dict:
        """Analyze price action patterns indicating smart money"""

        # Price efficiency (minimal gaps and erratic moves)
        daily_returns = data['close'].pct_change().dropna()
        return_smoothness = 1 / (daily_returns.std() + 0.01)

        # Support/resistance respect
        highs = data['high'].rolling(20).max()
        lows = data['low'].rolling(20).min()
        respect_levels = len(data[(data['high'] <= highs * 1.02) | (data['low'] >= lows * 0.98)]) / len(data)

        score = min(100, return_smoothness * 20 + respect_levels * 80)

        return {
            'return_smoothness': return_smoothness,
            'level_respect': respect_levels,
            'score': score,
            'pattern': 'Institutional price action' if score > 65 else 'Retail dominated'
        }

    def analyze_smart_money_timing(self, data: pd.DataFrame) -> Dict:
        """Analyze timing patterns of smart money"""

        # Consistent timing patterns (institutions trade at consistent times)
        # Using proxy of consistent volume patterns
        volume_consistency = 1 / (data['volume'].pct_change().std() + 0.01)

        # Early positioning (volume leading price)
        volume_ma = data['volume'].rolling(5).mean()
        price_ma = data['close'].rolling(5).mean()

        volume_leadership = (volume_ma.shift(1).corr(price_ma) > volume_ma.corr(price_ma))

        score = min(100, volume_consistency * 30 + (70 if volume_leadership else 30))

        return {
            'timing_consistency': volume_consistency,
            'volume_leads_price': volume_leadership,
            'score': score,
            'assessment': 'Smart timing patterns' if score > 60 else 'Random timing'
        }

    def analyze_accumulation_distribution_advanced(self, data: pd.DataFrame) -> Dict:
        """Advanced accumulation/distribution analysis"""

        # Money Flow Index (MFI)
        data['typical_price'] = (data['high'] + data['low'] + data['close']) / 3
        data['money_flow'] = data['typical_price'] * data['volume']

        # Separate positive and negative flows
        data['positive_flow'] = data['money_flow'].where(data['close'] > data['close'].shift(), 0)
        data['negative_flow'] = data['money_flow'].where(data['close'] <= data['close'].shift(), 0)

        # MFI calculation
        positive_mf = data['positive_flow'].rolling(14).sum()
        negative_mf = data['negative_flow'].rolling(14).sum()
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))

        current_mfi = mfi.iloc[-1] if not mfi.isna().iloc[-1] else 50
        mfi_trend = 'Accumulation' if current_mfi > 60 else 'Distribution' if current_mfi < 40 else 'Neutral'

        score = current_mfi if mfi_trend == 'Accumulation' else (100 - current_mfi) if mfi_trend == 'Distribution' else 50

        return {
            'money_flow_index': current_mfi,
            'trend': mfi_trend,
            'score': score,
            'interpretation': f'Smart money {mfi_trend.lower()} detected'
        }

    def determine_smart_money_flow(self, indicators: Dict) -> str:
        """Determine overall smart money flow direction"""

        scores = [indicator.get('score', 50) for indicator in indicators.values()]
        avg_score = sum(scores) / len(scores)

        if avg_score > 65:
            return 'Strong Inflow'
        elif avg_score > 55:
            return 'Moderate Inflow'
        elif avg_score < 35:
            return 'Strong Outflow'
        elif avg_score < 45:
            return 'Moderate Outflow'
        else:
            return 'Neutral'

    def generate_specific_trading_levels(self, technical: Dict, mm: Dict) -> Dict:
        """Generate specific entry and exit levels"""

        # Extract key levels from analyses
        levels = {
            'entry_levels': [],
            'exit_levels': [],
            'stop_loss': None,
            'targets': []
        }

        # From technical analysis
        if 'pattern_analysis' in technical:
            support_resistance = technical['pattern_analysis'].get('support_resistance', {})
            if support_resistance.get('nearest_support'):
                levels['entry_levels'].append({
                    'level': support_resistance['nearest_support'],
                    'type': 'support_bounce',
                    'confidence': 'medium'
                })
                levels['stop_loss'] = support_resistance['nearest_support'] * 0.97

            if support_resistance.get('nearest_resistance'):
                levels['targets'].append({
                    'level': support_resistance['nearest_resistance'],
                    'type': 'resistance_target',
                    'probability': 'high'
                })

        # From market maker analysis
        if 'entry_exit_signals' in mm:
            mm_signals = mm['entry_exit_signals']
            if mm_signals.get('target_levels'):
                for target in mm_signals['target_levels']:
                    levels['targets'].append({
                        'level': target,
                        'type': 'mm_target',
                        'probability': 'medium'
                    })

        return levels

    # Additional helper methods for grading and interpretation

    def grade_operations(self, score: float) -> str:
        """Grade operational performance"""
        if score >= 80: return 'A - Excellent Operations'
        elif score >= 70: return 'B - Strong Operations'
        elif score >= 60: return 'C - Average Operations'
        elif score >= 50: return 'D - Below Average Operations'
        else: return 'F - Poor Operations'

    def determine_composite_grade(self, score: float) -> str:
        """Determine overall investment grade"""
        if score >= 80: return 'A+ - Strong Buy'
        elif score >= 70: return 'A - Buy'
        elif score >= 60: return 'B+ - Moderate Buy'
        elif score >= 50: return 'B - Hold'
        elif score >= 40: return 'C - Weak Hold'
        else: return 'D - Sell'

    def interpret_composite_score(self, score: float) -> str:
        """Interpret what the composite score means"""
        if score >= 75:
            return "High-conviction investment opportunity with multiple positive factors aligned"
        elif score >= 65:
            return "Attractive investment with several favorable characteristics"
        elif score >= 55:
            return "Decent investment opportunity with some positive aspects"
        elif score >= 45:
            return "Mixed signals - requires careful consideration and monitoring"
        else:
            return "Multiple challenges identified - high risk investment"

    def identify_operational_strengths(self, metrics: Dict) -> List[str]:
        """Identify key operational strengths"""
        strengths = []

        if metrics.get('revenue_growth_proxy', {}).get('score', 0) > 70:
            strengths.append("Strong revenue growth trajectory")

        if metrics.get('operational_efficiency', {}).get('assessment') == 'High':
            strengths.append("High operational efficiency")

        if metrics.get('market_position', {}).get('position_strength') == 'Strong':
            strengths.append("Strong market position")

        return strengths

    def identify_operational_challenges(self, metrics: Dict) -> List[str]:
        """Identify key operational challenges"""
        challenges = []

        if metrics.get('revenue_growth_proxy', {}).get('trend') == 'Declining':
            challenges.append("Revenue decline trend")

        if metrics.get('operational_efficiency', {}).get('assessment') == 'Low':
            challenges.append("Operational efficiency concerns")

        if metrics.get('business_stability', {}).get('assessment') == 'Low':
            challenges.append("Business stability issues")

        return challenges

    def generate_operations_commentary(self, metrics: Dict, score: float) -> str:
        """Generate commentary on operational analysis"""
        commentary_parts = []

        if score > 70:
            commentary_parts.append("Company demonstrates strong operational performance")
        elif score > 50:
            commentary_parts.append("Company shows adequate operational metrics")
        else:
            commentary_parts.append("Operational challenges require attention")

        # Add specific insights
        revenue_trend = metrics.get('revenue_growth_proxy', {}).get('trend', 'Unknown')
        commentary_parts.append(f"Revenue proxy shows {revenue_trend.lower()} trend")

        return ". ".join(commentary_parts) + "."

    def generate_executive_summary(self, symbol: str, sector: str, technical: Dict,
                                 eic: Dict, mm: Dict, operations: Dict) -> Dict:
        """Generate executive summary combining all analyses"""

        composite = self.calculate_composite_score(technical, eic, mm, operations)

        # Key insights from each analysis
        key_insights = []

        # Technical insights
        tech_score = technical.get('executive_summary', {}).get('opportunity_score', 50)
        if tech_score > 70:
            key_insights.append("Strong technical setup with favorable momentum indicators")

        # EIC insights
        eic_score = eic.get('eic_score', 50)
        if eic_score > 70:
            key_insights.append("Favorable Environment-Infrastructure-Competitiveness profile")

        # Market maker insights
        smart_money_flow = mm.get('smart_money_analysis', {}).get('flow_direction', 'Neutral')
        if 'Inflow' in smart_money_flow:
            key_insights.append("Smart money accumulation detected")

        # Operations insights
        ops_score = operations.get('operations_score', 50)
        if ops_score > 65:
            key_insights.append("Strong operational metrics and business fundamentals")

        return {
            'investment_thesis': f"{symbol} ({sector}) presents a {composite['investment_grade'].lower()} opportunity",
            'composite_score': composite['composite_score'],
            'investment_grade': composite['investment_grade'],
            'key_insights': key_insights,
            'primary_catalysts': self.identify_catalysts(technical, eic, mm, operations),
            'key_risks': self.identify_key_risks(technical, eic, mm, operations),
            'recommended_action': self.recommend_action(composite['composite_score']),
            'time_horizon': self.suggest_time_horizon(mm, technical),
            'confidence_level': self.assess_overall_confidence(composite, key_insights)
        }

    def comprehensive_risk_assessment(self, technical: Dict, eic: Dict, mm: Dict) -> Dict:
        """Comprehensive risk assessment"""

        risks = {
            'technical_risks': [],
            'fundamental_risks': [],
            'market_structure_risks': [],
            'overall_risk_level': 'Medium',
            'risk_score': 50
        }

        risk_score = 0

        # Technical risks
        volatility = technical.get('pattern_analysis', {}).get('performance', {}).get('annualized_volatility', 25)
        if volatility > 40:
            risks['technical_risks'].append("High price volatility")
            risk_score += 20

        # EIC risks
        eic_score = eic.get('eic_score', 50)
        if eic_score < 40:
            risks['fundamental_risks'].append("Challenging EIC environment")
            risk_score += 15

        # Market structure risks
        liquidity_grade = mm.get('liquidity_provision', {}).get('liquidity_grade', '')
        if 'Poor' in liquidity_grade or 'Below Average' in liquidity_grade:
            risks['market_structure_risks'].append("Poor liquidity conditions")
            risk_score += 15

        risks['risk_score'] = min(100, risk_score)
        risks['overall_risk_level'] = 'High' if risk_score > 60 else 'Medium' if risk_score > 30 else 'Low'

        return risks

    def identify_time_sensitive_factors(self, mm: Dict, signals: Dict) -> Dict:
        """Identify time-sensitive factors requiring immediate attention"""

        time_sensitive = {
            'urgent_factors': [],
            'medium_term_factors': [],
            'long_term_factors': [],
            'monitoring_schedule': {}
        }

        # Check for urgent market maker signals
        current_phase = mm.get('current_market_phase', {}).get('current_phase', '')
        if current_phase in ['Markup', 'Distribution']:
            time_sensitive['urgent_factors'].append(f"Stock in {current_phase} phase - immediate attention required")

        # Check signal strength
        signal_strength = signals.get('overall_signal_strength', 0)
        if signal_strength > 75:
            time_sensitive['urgent_factors'].append("Strong trading signals - time-sensitive opportunity")

        return time_sensitive

    # Additional helper methods

    def assess_management_effectiveness(self, metrics: Dict) -> Dict:
        """Assess management effectiveness through operational proxies"""
        effectiveness_score = 50

        if metrics.get('operational_efficiency', {}).get('assessment') == 'High':
            effectiveness_score += 20

        if metrics.get('business_stability', {}).get('score', 0) > 70:
            effectiveness_score += 15

        return {
            'effectiveness_score': min(100, effectiveness_score),
            'assessment': 'High' if effectiveness_score > 70 else 'Medium' if effectiveness_score > 50 else 'Low',
            'key_indicators': ['operational_efficiency', 'business_stability', 'strategic_execution']
        }

    def assess_competitive_positioning(self, metrics: Dict, sector: str) -> Dict:
        """Assess competitive positioning within sector"""
        positioning_score = 50

        market_position = metrics.get('market_position', {})
        if market_position.get('position_strength') == 'Strong':
            positioning_score += 25

        if market_position.get('market_outperformance', False):
            positioning_score += 20

        return {
            'positioning_score': min(100, positioning_score),
            'competitive_strength': 'Strong' if positioning_score > 70 else 'Average' if positioning_score > 50 else 'Weak',
            'market_position': market_position.get('position_strength', 'Unknown'),
            'relative_performance': market_position.get('relative_performance', 0)
        }

    def assess_growth_trajectory(self, metrics: Dict) -> Dict:
        """Assess growth trajectory and sustainability"""
        growth_score = 50

        revenue_growth = metrics.get('revenue_growth_proxy', {}).get('score', 50)
        growth_score += (revenue_growth - 50) * 0.6

        operational_efficiency = metrics.get('operational_efficiency', {}).get('score', 50)
        growth_score += (operational_efficiency - 50) * 0.4

        return {
            'growth_score': max(0, min(100, growth_score)),
            'trajectory': 'Strong Growth' if growth_score > 70 else 'Moderate Growth' if growth_score > 50 else 'Limited Growth',
            'sustainability': 'High' if growth_score > 65 and operational_efficiency > 60 else 'Medium' if growth_score > 50 else 'Low'
        }

    def assess_smart_money_confidence(self, score: float, indicators: Dict) -> str:
        """Assess confidence level in smart money analysis"""
        confirmation_count = sum(1 for indicator in indicators.values() if indicator.get('score', 0) > 65)

        if score > 75 and confirmation_count >= 3:
            return 'Very High'
        elif score > 65 and confirmation_count >= 2:
            return 'High'
        elif score > 50:
            return 'Medium'
        else:
            return 'Low'

    def extract_key_smart_money_signals(self, indicators: Dict) -> List[str]:
        """Extract key smart money signals for summary"""
        signals = []

        for name, indicator in indicators.items():
            if indicator.get('score', 0) > 70:
                interpretation = indicator.get('interpretation', indicator.get('assessment', ''))
                if interpretation:
                    signals.append(f"{name.replace('_', ' ').title()}: {interpretation}")

        return signals[:3]  # Top 3 signals

    def recommend_smart_money_actions(self, score: float, flow_direction: str) -> List[str]:
        """Recommend actions based on smart money analysis"""
        actions = []

        if 'Strong Inflow' in flow_direction:
            actions.append("Consider accumulating position on market weakness")
            actions.append("Monitor for institutional buying patterns")
        elif 'Strong Outflow' in flow_direction:
            actions.append("Exercise caution - consider reducing exposure")
            actions.append("Wait for smart money re-entry signals")
        elif score > 60:
            actions.append("Monitor closely for directional confirmation")
        else:
            actions.append("Maintain current position and wait for clearer signals")

        return actions

    def identify_smart_money_monitoring_points(self, indicators: Dict) -> List[str]:
        """Identify key points to monitor for smart money activity"""
        monitoring_points = []

        volume_analysis = indicators.get('volume_analysis', {})
        if volume_analysis.get('large_block_frequency', 0) > 15:
            monitoring_points.append("Watch for unusual volume spikes indicating block trades")

        timing_patterns = indicators.get('timing_patterns', {})
        if timing_patterns.get('score', 0) > 60:
            monitoring_points.append("Monitor consistent timing patterns for institutional activity")

        accumulation = indicators.get('accumulation_distribution', {})
        if accumulation.get('trend') != 'Neutral':
            monitoring_points.append(f"Track {accumulation.get('trend', '').lower()} pattern continuation")

        return monitoring_points

    def identify_catalysts(self, technical: Dict, eic: Dict, mm: Dict, operations: Dict) -> List[str]:
        """Identify potential catalysts that could drive stock performance"""
        catalysts = []

        # Technical catalysts
        momentum = technical.get('pattern_analysis', {}).get('momentum', {})
        if momentum.get('momentum_score', 0) > 70:
            catalysts.append("Strong technical momentum building")

        # Smart money catalysts
        if mm.get('smart_money_analysis', {}).get('flow_direction') == 'Strong Inflow':
            catalysts.append("Institutional accumulation accelerating")

        # Operational catalysts
        if operations.get('operations_score', 0) > 70:
            catalysts.append("Strong operational performance providing fundamental support")

        return catalysts

    def identify_key_risks(self, technical: Dict, eic: Dict, mm: Dict, operations: Dict) -> List[str]:
        """Identify key investment risks"""
        risks = []

        # Volatility risk
        volatility = technical.get('pattern_analysis', {}).get('performance', {}).get('annualized_volatility', 0)
        if volatility > 35:
            risks.append("High volatility risk")

        # Liquidity risk
        liquidity_grade = mm.get('liquidity_provision', {}).get('liquidity_grade', '')
        if 'Poor' in liquidity_grade:
            risks.append("Poor liquidity conditions")

        # Fundamental risk
        if eic.get('eic_score', 50) < 45:
            risks.append("Challenging fundamental environment")

        return risks

    def recommend_action(self, composite_score: float) -> str:
        """Recommend investment action based on composite score"""
        if composite_score >= 75:
            return "Strong Buy - High conviction opportunity"
        elif composite_score >= 65:
            return "Buy - Attractive investment opportunity"
        elif composite_score >= 55:
            return "Moderate Buy - Consider position building"
        elif composite_score >= 45:
            return "Hold - Monitor for improvement"
        else:
            return "Avoid/Sell - Multiple risk factors identified"

    def suggest_time_horizon(self, mm: Dict, technical: Dict) -> str:
        """Suggest appropriate investment time horizon"""
        current_phase = mm.get('current_market_phase', {}).get('current_phase', '')

        if current_phase == 'Accumulation':
            return "Medium-term (3-6 months)"
        elif current_phase == 'Markup':
            return "Short-term (1-3 months)"
        elif technical.get('pattern_analysis', {}).get('trend_analysis', {}).get('overall_trend') == 'Bullish':
            return "Medium-term (3-6 months)"
        else:
            return "Short-term (1-2 months) or wait for better setup"

    def assess_overall_confidence(self, composite: Dict, insights: List[str]) -> str:
        """Assess overall confidence in the analysis"""
        score = composite.get('composite_score', 50)
        insight_count = len(insights)

        if score > 70 and insight_count >= 3:
            return "High"
        elif score > 60 and insight_count >= 2:
            return "Medium-High"
        elif score > 50:
            return "Medium"
        else:
            return "Low"

if __name__ == "__main__":
    reporter = ComprehensiveStockReporter()

    # Test comprehensive report generation
    test_symbol = "VCB"
    test_sector = "Banks"

    print(f"🚀 GENERATING COMPREHENSIVE REPORT FOR {test_symbol}")
    print("=" * 60)

    report = reporter.generate_comprehensive_report(test_symbol, test_sector)

    if 'error' not in report:
        print(f"✅ Report generated successfully!")
        print(f"Composite Score: {report['composite_score']['composite_score']:.1f}")
        print(f"Investment Grade: {report['composite_score']['investment_grade']}")
        print(f"Recommended Action: {report['executive_summary']['recommended_action']}")

        # Save comprehensive report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'/workspaces/BMAD-METHOD/session_logs/comprehensive_report_{test_symbol}_{timestamp}.json'

        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        print(f"\n💾 Comprehensive report saved to: {filename}")
    else:
        print(f"❌ Error generating report: {report['error']}")

    print("\n🎯 Comprehensive Stock Analysis System Ready!")
    print("Features:")
    print("• Deep technical analysis with 52-week patterns")
    print("• EIC framework for top-down analysis")
    print("• Market maker behavior analysis")
    print("• Company operations assessment")
    print("• Smart money flow tracking")
    print("• Advanced entry/exit signals")
    print("• Comprehensive risk assessment")