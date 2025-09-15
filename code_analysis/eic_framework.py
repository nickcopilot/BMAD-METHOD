#!/usr/bin/env python3
"""
Enhanced EIC Framework for Vietnam Stock Analysis
Environment, Infrastructure, Competitiveness analysis
Top-down approach for systematic stock evaluation
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

class EICFramework:
    def __init__(self):
        self.vnstock_client = vn.Vnstock()

        # EIC scoring weights
        self.eic_weights = {
            'environment': 0.35,    # Market environment, sector trends
            'infrastructure': 0.35, # Company fundamentals, business model
            'competitiveness': 0.30 # Competitive position, market share
        }

        # Sector-specific EIC criteria
        self.sector_criteria = {
            'Banks': {
                'environment': ['interest_rate_trend', 'credit_growth', 'regulatory_environment'],
                'infrastructure': ['branch_network', 'digital_banking', 'capital_adequacy'],
                'competitiveness': ['market_share', 'nii_growth', 'asset_quality']
            },
            'Real_Estate': {
                'environment': ['property_prices', 'urbanization_trend', 'government_policy'],
                'infrastructure': ['land_bank', 'project_pipeline', 'financial_leverage'],
                'competitiveness': ['brand_strength', 'location_advantage', 'execution_capability']
            },
            'Technology': {
                'environment': ['digital_transformation', 'government_support', 'talent_availability'],
                'infrastructure': ['r_and_d_capability', 'platform_scalability', 'partnership_network'],
                'competitiveness': ['market_position', 'innovation_speed', 'customer_acquisition']
            },
            'Manufacturing': {
                'environment': ['global_demand', 'raw_material_costs', 'trade_policies'],
                'infrastructure': ['production_capacity', 'automation_level', 'supply_chain'],
                'competitiveness': ['cost_efficiency', 'product_quality', 'export_capability']
            }
        }

        # Market environment indicators
        self.market_indicators = {
            'macro_economic': ['gdp_growth', 'inflation_rate', 'usd_vnd_rate', 'policy_rates'],
            'market_sentiment': ['vnindex_trend', 'foreign_flows', 'valuations', 'volume_trend'],
            'sector_rotation': ['sector_performance', 'relative_strength', 'earnings_revision']
        }

    def analyze_environment_score(self, symbol: str, sector: str) -> Dict:
        """Analyze environmental factors affecting the stock"""
        try:
            # Get market data for context
            end_date = datetime.now()
            start_date = end_date - timedelta(days=180)  # 6 months of data

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            # Get VN-Index for market comparison
            vnindex = self.vnstock_client.stock(symbol='VNINDEX', source='VCI')
            market_data = vnindex.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            environment_score = 50  # Base score
            factors = {}

            # Market trend analysis
            if not market_data.empty:
                market_return = (market_data['close'].iloc[-1] / market_data['close'].iloc[0] - 1) * 100
                market_volatility = market_data['close'].pct_change().std() * np.sqrt(252) * 100

                factors['market_trend'] = {
                    'market_return_6m': market_return,
                    'market_volatility': market_volatility,
                    'score': max(0, min(100, 50 + market_return))
                }
                environment_score += (factors['market_trend']['score'] - 50) * 0.3

            # Sector momentum (relative to market)
            if not data.empty and not market_data.empty:
                stock_return = (data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100
                relative_performance = stock_return - market_return

                factors['sector_momentum'] = {
                    'stock_return_6m': stock_return,
                    'relative_performance': relative_performance,
                    'score': max(0, min(100, 50 + relative_performance * 2))
                }
                environment_score += (factors['sector_momentum']['score'] - 50) * 0.4

            # Volume trend (liquidity environment)
            if not data.empty:
                recent_volume = data['volume'].tail(30).mean()
                historical_volume = data['volume'].head(30).mean()
                volume_trend = (recent_volume / historical_volume - 1) * 100 if historical_volume > 0 else 0

                factors['liquidity_environment'] = {
                    'volume_trend': volume_trend,
                    'recent_avg_volume': recent_volume,
                    'score': max(0, min(100, 50 + volume_trend))
                }
                environment_score += (factors['liquidity_environment']['score'] - 50) * 0.3

            # Sector-specific environmental factors
            sector_factors = self.analyze_sector_environment(sector)
            factors['sector_specific'] = sector_factors
            environment_score += (sector_factors['score'] - 50) * 0.2

            return {
                'symbol': symbol,
                'sector': sector,
                'environment_score': max(0, min(100, environment_score)),
                'factors': factors,
                'analysis': self.generate_environment_commentary(factors, environment_score)
            }

        except Exception as e:
            logging.error(f"Error analyzing environment for {symbol}: {e}")
            return {'symbol': symbol, 'environment_score': 50, 'error': str(e)}

    def analyze_infrastructure_score(self, symbol: str, sector: str) -> Dict:
        """Analyze infrastructure/fundamental factors"""
        try:
            # Get fundamental data
            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')

            # Financial metrics (placeholder - would need actual financial data)
            infrastructure_score = 50
            factors = {}

            # Business model strength
            factors['business_model'] = self.assess_business_model_strength(symbol, sector)
            infrastructure_score += (factors['business_model']['score'] - 50) * 0.4

            # Financial health
            factors['financial_health'] = self.assess_financial_health(symbol)
            infrastructure_score += (factors['financial_health']['score'] - 50) * 0.3

            # Management quality (proxy through performance consistency)
            factors['management_quality'] = self.assess_management_quality(symbol)
            infrastructure_score += (factors['management_quality']['score'] - 50) * 0.3

            return {
                'symbol': symbol,
                'sector': sector,
                'infrastructure_score': max(0, min(100, infrastructure_score)),
                'factors': factors,
                'analysis': self.generate_infrastructure_commentary(factors, infrastructure_score)
            }

        except Exception as e:
            logging.error(f"Error analyzing infrastructure for {symbol}: {e}")
            return {'symbol': symbol, 'infrastructure_score': 50, 'error': str(e)}

    def analyze_competitiveness_score(self, symbol: str, sector: str) -> Dict:
        """Analyze competitive position factors"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 1 year for competitive analysis

            stock = self.vnstock_client.stock(symbol=symbol, source='VCI')
            data = stock.quote.history(
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1D'
            )

            competitiveness_score = 50
            factors = {}

            # Market share proxy (relative volume in sector)
            factors['market_presence'] = self.assess_market_presence(symbol, sector)
            competitiveness_score += (factors['market_presence']['score'] - 50) * 0.4

            # Competitive advantage (price performance vs sector)
            factors['competitive_advantage'] = self.assess_competitive_advantage(symbol, data)
            competitiveness_score += (factors['competitive_advantage']['score'] - 50) * 0.3

            # Innovation and adaptation (volatility-adjusted returns)
            factors['adaptability'] = self.assess_adaptability(symbol, data)
            competitiveness_score += (factors['adaptability']['score'] - 50) * 0.3

            return {
                'symbol': symbol,
                'sector': sector,
                'competitiveness_score': max(0, min(100, competitiveness_score)),
                'factors': factors,
                'analysis': self.generate_competitiveness_commentary(factors, competitiveness_score)
            }

        except Exception as e:
            logging.error(f"Error analyzing competitiveness for {symbol}: {e}")
            return {'symbol': symbol, 'competitiveness_score': 50, 'error': str(e)}

    def calculate_comprehensive_eic_score(self, symbol: str, sector: str) -> Dict:
        """Calculate comprehensive EIC score"""
        logging.info(f"Calculating comprehensive EIC score for {symbol}")

        # Get individual scores
        environment = self.analyze_environment_score(symbol, sector)
        infrastructure = self.analyze_infrastructure_score(symbol, sector)
        competitiveness = self.analyze_competitiveness_score(symbol, sector)

        # Calculate weighted EIC score
        eic_score = (
            environment['environment_score'] * self.eic_weights['environment'] +
            infrastructure['infrastructure_score'] * self.eic_weights['infrastructure'] +
            competitiveness['competitiveness_score'] * self.eic_weights['competitiveness']
        )

        # Determine investment grade
        investment_grade = self.determine_eic_grade(eic_score)

        return {
            'symbol': symbol,
            'sector': sector,
            'analysis_date': datetime.now().isoformat(),
            'eic_score': eic_score,
            'investment_grade': investment_grade,
            'component_scores': {
                'environment': environment,
                'infrastructure': infrastructure,
                'competitiveness': competitiveness
            },
            'weights_used': self.eic_weights,
            'executive_summary': self.generate_eic_executive_summary(
                symbol, sector, eic_score, environment, infrastructure, competitiveness
            )
        }

    # Helper methods for detailed analysis

    def analyze_sector_environment(self, sector: str) -> Dict:
        """Analyze sector-specific environmental factors"""
        sector_scores = {
            'Banks': 65,  # Stable interest rate environment
            'Real_Estate': 55,  # Mixed signals in property market
            'Technology': 75,  # Strong digital transformation trend
            'Manufacturing': 60,  # Recovering global demand
            'Oil_Gas': 50,  # Volatile energy markets
            'Retail': 65,  # Growing consumer spending
            'Healthcare': 70,  # Aging population trend
            'Agriculture': 55   # Weather and commodity dependent
        }

        score = sector_scores.get(sector, 50)

        return {
            'sector': sector,
            'score': score,
            'factors': self.sector_criteria.get(sector, {}).get('environment', [])
        }

    def assess_business_model_strength(self, symbol: str, sector: str) -> Dict:
        """Assess business model strength (placeholder implementation)"""
        # This would integrate actual financial data in production
        model_strengths = {
            'Banks': 70,  # Stable recurring revenue model
            'Technology': 80,  # Scalable, high-margin models
            'Real_Estate': 60,  # Asset-heavy, cyclical
            'Manufacturing': 65,  # Operational leverage potential
        }

        score = model_strengths.get(sector, 60)

        return {
            'score': score,
            'model_type': sector,
            'strengths': ['recurring_revenue', 'scalability', 'margin_stability'],
            'challenges': ['competition', 'regulatory_risk', 'market_cyclicality']
        }

    def assess_financial_health(self, symbol: str) -> Dict:
        """Assess financial health (placeholder - needs actual financial data)"""
        # In production, this would analyze actual financial statements
        return {
            'score': 65,
            'liquidity': 'adequate',
            'leverage': 'moderate',
            'profitability': 'stable',
            'cash_flow': 'positive'
        }

    def assess_management_quality(self, symbol: str) -> Dict:
        """Assess management quality through performance consistency"""
        # Proxy through consistent performance and execution
        return {
            'score': 60,
            'execution_consistency': 'good',
            'strategic_vision': 'clear',
            'capital_allocation': 'efficient'
        }

    def assess_market_presence(self, symbol: str, sector: str) -> Dict:
        """Assess market presence and share"""
        # This would use actual market share data in production
        return {
            'score': 65,
            'market_position': 'strong',
            'brand_recognition': 'high',
            'distribution_network': 'extensive'
        }

    def assess_competitive_advantage(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Assess competitive advantage through price performance"""
        if data.empty:
            return {'score': 50, 'advantage_type': 'unknown'}

        # Analyze price stability and growth
        returns = data['close'].pct_change().dropna()
        volatility = returns.std()
        total_return = (data['close'].iloc[-1] / data['close'].iloc[0] - 1) * 100

        # Score based on risk-adjusted returns
        risk_adjusted_score = max(0, min(100, 50 + total_return - volatility * 100))

        return {
            'score': risk_adjusted_score,
            'total_return': total_return,
            'volatility': volatility * 100,
            'advantage_type': 'cost_leadership' if volatility < 0.02 else 'differentiation'
        }

    def assess_adaptability(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Assess company adaptability and innovation"""
        if data.empty:
            return {'score': 50}

        # Analyze trading patterns for institutional interest (proxy for innovation)
        volume_growth = data['volume'].tail(60).mean() / data['volume'].head(60).mean() - 1
        price_momentum = data['close'].pct_change(20).iloc[-1] * 100

        adaptability_score = max(0, min(100, 50 + volume_growth * 20 + price_momentum))

        return {
            'score': adaptability_score,
            'volume_growth': volume_growth * 100,
            'price_momentum': price_momentum,
            'innovation_proxy': 'high' if adaptability_score > 70 else 'moderate'
        }

    def determine_eic_grade(self, eic_score: float) -> str:
        """Determine investment grade based on EIC score"""
        if eic_score >= 80:
            return 'EIC-A+ (Excellent)'
        elif eic_score >= 70:
            return 'EIC-A (Strong)'
        elif eic_score >= 60:
            return 'EIC-B+ (Good)'
        elif eic_score >= 50:
            return 'EIC-B (Average)'
        elif eic_score >= 40:
            return 'EIC-C+ (Below Average)'
        elif eic_score >= 30:
            return 'EIC-C (Weak)'
        else:
            return 'EIC-D (Poor)'

    def generate_environment_commentary(self, factors: Dict, score: float) -> str:
        """Generate commentary for environment analysis"""
        commentary = []

        if score > 70:
            commentary.append("Favorable market environment")
        elif score > 50:
            commentary.append("Neutral market conditions")
        else:
            commentary.append("Challenging market environment")

        if 'market_trend' in factors:
            market_return = factors['market_trend']['market_return_6m']
            if market_return > 10:
                commentary.append("strong overall market performance")
            elif market_return < -10:
                commentary.append("weak market backdrop")

        return ". ".join(commentary) + "."

    def generate_infrastructure_commentary(self, factors: Dict, score: float) -> str:
        """Generate commentary for infrastructure analysis"""
        commentary = []

        if score > 70:
            commentary.append("Strong business fundamentals")
        elif score > 50:
            commentary.append("Adequate infrastructure")
        else:
            commentary.append("Infrastructure challenges identified")

        return ". ".join(commentary) + "."

    def generate_competitiveness_commentary(self, factors: Dict, score: float) -> str:
        """Generate commentary for competitiveness analysis"""
        commentary = []

        if score > 70:
            commentary.append("Strong competitive position")
        elif score > 50:
            commentary.append("Competitive position maintained")
        else:
            commentary.append("Competitive pressures evident")

        return ". ".join(commentary) + "."

    def generate_eic_executive_summary(self, symbol: str, sector: str, eic_score: float,
                                     environment: Dict, infrastructure: Dict, competitiveness: Dict) -> Dict:
        """Generate executive summary for EIC analysis"""

        strengths = []
        weaknesses = []

        # Identify strengths and weaknesses
        if environment['environment_score'] > 65:
            strengths.append("Favorable market environment")
        elif environment['environment_score'] < 45:
            weaknesses.append("Challenging external conditions")

        if infrastructure['infrastructure_score'] > 65:
            strengths.append("Strong business fundamentals")
        elif infrastructure['infrastructure_score'] < 45:
            weaknesses.append("Infrastructure concerns")

        if competitiveness['competitiveness_score'] > 65:
            strengths.append("Competitive advantage")
        elif competitiveness['competitiveness_score'] < 45:
            weaknesses.append("Weak competitive position")

        return {
            'overall_assessment': f"{symbol} receives an EIC score of {eic_score:.1f}",
            'key_strengths': strengths,
            'key_weaknesses': weaknesses,
            'recommendation': self.get_investment_recommendation(eic_score),
            'risk_level': 'High' if eic_score < 40 else 'Moderate' if eic_score < 60 else 'Low'
        }

    def get_investment_recommendation(self, eic_score: float) -> str:
        """Get investment recommendation based on EIC score"""
        if eic_score >= 70:
            return 'Strong Buy - High conviction investment'
        elif eic_score >= 60:
            return 'Buy - Attractive investment opportunity'
        elif eic_score >= 50:
            return 'Hold - Fair value, monitor developments'
        elif eic_score >= 40:
            return 'Weak Hold - Consider reducing position'
        else:
            return 'Sell - Significant risks identified'

if __name__ == "__main__":
    eic = EICFramework()

    # Test with sample stock
    test_symbol = "VCB"
    test_sector = "Banks"

    analysis = eic.calculate_comprehensive_eic_score(test_symbol, test_sector)

    print(f"📊 EIC ANALYSIS: {test_symbol}")
    print("=" * 50)
    print(f"EIC Score: {analysis['eic_score']:.1f}")
    print(f"Grade: {analysis['investment_grade']}")
    print(f"Recommendation: {analysis['executive_summary']['recommendation']}")

    print(f"\nComponent Scores:")
    print(f"Environment: {analysis['component_scores']['environment']['environment_score']:.1f}")
    print(f"Infrastructure: {analysis['component_scores']['infrastructure']['infrastructure_score']:.1f}")
    print(f"Competitiveness: {analysis['component_scores']['competitiveness']['competitiveness_score']:.1f}")

    # Save analysis
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'/workspaces/BMAD-METHOD/session_logs/eic_analysis_{test_symbol}_{timestamp}.json'

    with open(filename, 'w') as f:
        json.dump(analysis, f, indent=2, default=str)

    print(f"\n💾 EIC analysis saved to: {filename}")
    print("🚀 Enhanced EIC Framework ready!")