#!/usr/bin/env python3
"""
Cross-Stock Signal Correlation Analysis
Analyze correlations between smart money signals across Vietnamese stocks and sectors
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '.'))

from shared.analysis.smart_money import SmartMoneyAnalyzer
from shared.models.database import get_db

def collect_signal_data():
    """Collect signal data for all stocks across multiple timeframes"""
    print("=== Collecting Cross-Stock Signal Data ===")

    analyzer = SmartMoneyAnalyzer()
    db = get_db()

    all_stocks = db.get_all_stocks()
    print(f"Analyzing signal correlations for {len(all_stocks)} stocks")

    # Collect signals for different timeframes
    timeframes = [30, 60, 90]
    signal_matrix = {}

    for timeframe in timeframes:
        print(f"\n📊 Collecting {timeframe}-day signals...")

        timeframe_data = {}
        for stock in all_stocks:
            symbol = stock['symbol']
            print(f"  🔍 {symbol}...", end=' ')

            try:
                analysis = analyzer.analyze_symbol(symbol, days_back=timeframe)

                if 'error' not in analysis:
                    signal_data = {
                        'score': analysis['composite_score']['composite_score'],
                        'adjusted_score': analysis['market_context']['adjusted_score'],
                        'signal_class': analysis['composite_score']['signal_class'],
                        'volume_score': analysis['composite_score']['component_scores']['volume'],
                        'price_action_score': analysis['composite_score']['component_scores']['price_action'],
                        'momentum_score': analysis['composite_score']['component_scores']['momentum'],
                        'accumulation_score': analysis['composite_score']['component_scores']['accumulation'],
                        'smart_money_flow_score': analysis['composite_score']['component_scores']['smart_money_flow'],
                        'sector': stock['sector']
                    }
                    timeframe_data[symbol] = signal_data
                    print(f"{signal_data['adjusted_score']:.1f}")
                else:
                    print(f"Error: {analysis['error']}")

            except Exception as e:
                print(f"Failed: {e}")

        signal_matrix[timeframe] = timeframe_data

    return signal_matrix

def analyze_correlations(signal_matrix):
    """Analyze correlations between stocks and components"""
    print(f"\n=== Analyzing Signal Correlations ===")

    correlation_results = {}

    for timeframe, data in signal_matrix.items():
        print(f"\n📈 {timeframe}-Day Correlations:")

        if len(data) < 3:
            print("  ⚠️ Insufficient data for correlation analysis")
            continue

        # Create DataFrame for correlation analysis
        symbols = list(data.keys())

        # Overall adjusted scores correlation
        score_data = {symbol: info['adjusted_score'] for symbol, info in data.items()}
        score_df = pd.DataFrame([score_data])

        # Component correlations
        components = ['volume_score', 'price_action_score', 'momentum_score', 'accumulation_score', 'smart_money_flow_score']
        component_data = {}

        for component in components:
            component_data[component] = {symbol: info[component] for symbol, info in data.items()}

        component_df = pd.DataFrame(component_data, index=symbols)

        # Calculate correlations
        score_corr = pd.DataFrame(score_data, index=[0]).T.corr()
        component_corr = component_df.corr()

        # Sector correlations
        sector_scores = {}
        for symbol, info in data.items():
            sector = info['sector']
            if sector not in sector_scores:
                sector_scores[sector] = []
            sector_scores[sector].append(info['adjusted_score'])

        # Average sector scores
        sector_averages = {sector: np.mean(scores) for sector, scores in sector_scores.items()}

        correlation_results[timeframe] = {
            'score_correlations': score_corr,
            'component_correlations': component_corr,
            'sector_averages': sector_averages,
            'sector_scores': sector_scores,
            'stock_data': data
        }

        # Display key findings
        print(f"  📊 Analyzed {len(symbols)} stocks")
        print(f"  🏢 Sectors: {len(sector_averages)}")

        # Component correlation summary
        print(f"  🔗 Component Correlations (highest):")
        for i, component in enumerate(components):
            for j, other_component in enumerate(components):
                if i < j:  # Avoid duplicates
                    corr_value = component_corr.loc[component, other_component]
                    if abs(corr_value) > 0.3:  # Show significant correlations
                        print(f"    {component} ↔ {other_component}: {corr_value:.2f}")

        # Sector performance
        print(f"  🏆 Sector Rankings:")
        sorted_sectors = sorted(sector_averages.items(), key=lambda x: x[1], reverse=True)
        for sector, avg_score in sorted_sectors:
            print(f"    {sector.replace('_', ' ').title()}: {avg_score:.1f}")

    return correlation_results

def find_signal_patterns(correlation_results):
    """Find patterns and insights across timeframes"""
    print(f"\n=== Pattern Analysis ===")

    insights = {
        'consistent_performers': {},
        'sector_trends': {},
        'component_patterns': {},
        'timeframe_stability': {}
    }

    # Find stocks that perform consistently across timeframes
    all_stocks = set()
    for timeframe_data in correlation_results.values():
        all_stocks.update(timeframe_data['stock_data'].keys())

    print(f"📈 Consistent Performers Analysis:")
    for symbol in all_stocks:
        scores = []
        signal_classes = []

        for timeframe, data in correlation_results.items():
            if symbol in data['stock_data']:
                scores.append(data['stock_data'][symbol]['adjusted_score'])
                signal_classes.append(data['stock_data'][symbol]['signal_class'])

        if len(scores) >= 2:  # At least 2 timeframes
            score_variance = np.var(scores)
            avg_score = np.mean(scores)
            signal_consistency = len(set(signal_classes))

            insights['consistent_performers'][symbol] = {
                'average_score': avg_score,
                'score_variance': score_variance,
                'signal_consistency': signal_consistency,
                'scores': scores,
                'signals': signal_classes
            }

            if score_variance < 5 and avg_score > 55:  # Low variance, good score
                print(f"  ✅ {symbol}: Consistently strong ({avg_score:.1f} ± {score_variance:.1f})")
            elif score_variance < 5 and avg_score < 50:  # Low variance, weak score
                print(f"  ⚠️ {symbol}: Consistently weak ({avg_score:.1f} ± {score_variance:.1f})")

    # Analyze sector trends across timeframes
    print(f"\n🏢 Sector Trend Analysis:")
    for sector in ['banking', 'real_estate', 'steel', 'securities']:
        sector_trends = []

        for timeframe, data in correlation_results.items():
            if sector in data['sector_averages']:
                sector_trends.append(data['sector_averages'][sector])

        if sector_trends:
            trend_direction = "improving" if sector_trends[-1] > sector_trends[0] else "declining"
            avg_performance = np.mean(sector_trends)

            insights['sector_trends'][sector] = {
                'trends': sector_trends,
                'direction': trend_direction,
                'average': avg_performance
            }

            print(f"  {sector.replace('_', ' ').title()}: {avg_performance:.1f} ({trend_direction})")

    # Component pattern analysis
    print(f"\n🔬 Component Pattern Analysis:")
    all_components = ['volume_score', 'price_action_score', 'momentum_score', 'accumulation_score', 'smart_money_flow_score']

    for component in all_components:
        component_correlations = []

        for timeframe, data in correlation_results.items():
            if 'component_correlations' in data:
                corr_matrix = data['component_correlations']
                # Average correlation with other components
                other_components = [c for c in all_components if c != component]
                avg_corr = np.mean([abs(corr_matrix.loc[component, other]) for other in other_components if other in corr_matrix.columns])
                component_correlations.append(avg_corr)

        if component_correlations:
            avg_correlation = np.mean(component_correlations)
            insights['component_patterns'][component] = avg_correlation

            correlation_strength = "High" if avg_correlation > 0.5 else "Medium" if avg_correlation > 0.3 else "Low"
            print(f"  {component.replace('_', ' ').title()}: {correlation_strength} correlation ({avg_correlation:.2f})")

    return insights

def generate_correlation_report(correlation_results, insights):
    """Generate comprehensive correlation analysis report"""
    print(f"\n=== Cross-Stock Signal Correlation Report ===")

    # Overall system assessment
    total_stocks = len(set().union(*[data['stock_data'].keys() for data in correlation_results.values()]))
    timeframes_analyzed = len(correlation_results)

    print(f"📊 Analysis Scope:")
    print(f"  • Total Stocks: {total_stocks}")
    print(f"  • Timeframes: {timeframes_analyzed}")
    print(f"  • Sectors: {len(insights['sector_trends'])}")

    # Key findings
    print(f"\n🔍 Key Findings:")

    # Top consistent performers
    if insights['consistent_performers']:
        consistent_stocks = {k: v for k, v in insights['consistent_performers'].items()
                           if v['score_variance'] < 5 and v['average_score'] > 55}

        if consistent_stocks:
            print(f"  ✅ Consistent Strong Performers:")
            for symbol, data in sorted(consistent_stocks.items(), key=lambda x: x[1]['average_score'], reverse=True)[:5]:
                print(f"    {symbol}: {data['average_score']:.1f} (variance: {data['score_variance']:.1f})")

    # Sector performance ranking
    if insights['sector_trends']:
        print(f"  🏆 Sector Performance Ranking:")
        sorted_sectors = sorted(insights['sector_trends'].items(), key=lambda x: x[1]['average'], reverse=True)
        for i, (sector, data) in enumerate(sorted_sectors, 1):
            trend_icon = "📈" if data['direction'] == "improving" else "📉"
            print(f"    {i}. {sector.replace('_', ' ').title()}: {data['average']:.1f} {trend_icon}")

    # Component analysis
    if insights['component_patterns']:
        print(f"  🔬 Component Correlation Strength:")
        sorted_components = sorted(insights['component_patterns'].items(), key=lambda x: x[1], reverse=True)
        for component, correlation in sorted_components:
            strength = "Strong" if correlation > 0.5 else "Moderate" if correlation > 0.3 else "Weak"
            print(f"    {component.replace('_', ' ').title()}: {strength} ({correlation:.2f})")

    # Quality assessment
    print(f"\n🎯 System Quality Assessment:")

    # Signal diversity
    all_signals = set()
    for data in correlation_results.values():
        for stock_info in data['stock_data'].values():
            all_signals.add(stock_info['signal_class'])

    signal_diversity = len(all_signals)

    # Score range
    all_scores = []
    for data in correlation_results.values():
        for stock_info in data['stock_data'].values():
            all_scores.append(stock_info['adjusted_score'])

    score_range = max(all_scores) - min(all_scores) if all_scores else 0

    print(f"  • Signal Diversity: {signal_diversity} types ({', '.join(all_signals)})")
    print(f"  • Score Range: {score_range:.1f} points")
    print(f"  • Total Analysis Points: {len(all_scores)}")

    # Overall quality
    if signal_diversity >= 3 and score_range > 20:
        quality = "EXCELLENT"
    elif signal_diversity >= 2 and score_range > 15:
        quality = "GOOD"
    elif score_range > 10:
        quality = "FAIR"
    else:
        quality = "NEEDS IMPROVEMENT"

    print(f"  • Overall Quality: {quality}")

    return {
        'total_stocks': total_stocks,
        'signal_diversity': signal_diversity,
        'score_range': score_range,
        'quality': quality,
        'consistent_performers': len([k for k, v in insights['consistent_performers'].items()
                                    if v['score_variance'] < 5 and v['average_score'] > 55])
    }

def main():
    """Main correlation analysis execution"""
    print("Vietnam Stock Analysis - Cross-Stock Signal Correlation")
    print("=" * 70)

    try:
        # Phase 1: Collect signal data across timeframes
        signal_matrix = collect_signal_data()

        # Phase 2: Analyze correlations
        correlation_results = analyze_correlations(signal_matrix)

        # Phase 3: Find patterns and insights
        insights = find_signal_patterns(correlation_results)

        # Phase 4: Generate comprehensive report
        summary = generate_correlation_report(correlation_results, insights)

        print("\n" + "=" * 70)

        if summary['quality'] in ['EXCELLENT', 'GOOD']:
            print("🎉 CORRELATION ANALYSIS: SUCCESSFUL!")
            print(f"\n✅ Achievements:")
            print(f"  • Analyzed {summary['total_stocks']} stocks across multiple timeframes")
            print(f"  • {summary['signal_diversity']} distinct signal classifications")
            print(f"  • {summary['score_range']:.1f} point signal range")
            print(f"  • {summary['consistent_performers']} consistent performers identified")
            print(f"  • Quality Assessment: {summary['quality']}")

            print(f"\n🚀 Cross-Stock Analysis Complete:")
            print(f"  • Multi-timeframe signal consistency verified")
            print(f"  • Sector correlation patterns identified")
            print(f"  • Component interaction analysis complete")
            print(f"  • Vietnamese market behavior understanding enhanced")

        else:
            print("⚠️ CORRELATION ANALYSIS: PARTIALLY SUCCESSFUL")
            print(f"  • Quality: {summary['quality']}")
            print(f"  • May benefit from additional calibration")

    except Exception as e:
        print(f"❌ Correlation analysis error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()