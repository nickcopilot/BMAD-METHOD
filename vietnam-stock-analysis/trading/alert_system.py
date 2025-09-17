#!/usr/bin/env python3
"""
Automated Alert System
High-probability setup alerts for Vietnamese market trading
"""

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from shared.models.database import get_db
from shared.analysis.smart_money import SmartMoneyAnalyzer
from trading.risk_manager import VietnameseRiskManager

class VietnameseAlertSystem:
    """Automated alert system for Vietnamese stock trading opportunities"""

    def __init__(self):
        self.db = get_db()
        self.analyzer = SmartMoneyAnalyzer()
        self.risk_manager = VietnameseRiskManager()

        # Alert configuration
        self.alert_config = {
            'scan_frequency_minutes': 15,      # Scan every 15 minutes
            'min_signal_strength': 65,         # Minimum signal strength for alerts
            'min_confidence': 0.75,            # Minimum confidence level
            'min_risk_reward': 2.5,            # Minimum risk-reward ratio
            'max_portfolio_risk': 0.15,        # Maximum portfolio risk before alerts
            'volume_surge_threshold': 2.0,     # Volume surge multiplier
            'breakout_threshold': 0.02,        # 2% breakout threshold
            'alert_cooldown_hours': 4,         # Hours between alerts for same stock
            'max_alerts_per_day': 10           # Maximum alerts per day
        }

        # Alert types
        self.alert_types = {
            'STRONG_BUY': {
                'priority': 'HIGH',
                'min_strength': 75,
                'description': 'Strong institutional buying detected'
            },
            'BREAKOUT_BUY': {
                'priority': 'HIGH',
                'min_strength': 65,
                'description': 'Bullish breakout with volume confirmation'
            },
            'ACCUMULATION_ZONE': {
                'priority': 'MEDIUM',
                'min_strength': 60,
                'description': 'Smart money accumulation detected'
            },
            'OVERSOLD_BOUNCE': {
                'priority': 'MEDIUM',
                'min_strength': 55,
                'description': 'Oversold bounce opportunity'
            },
            'RISK_WARNING': {
                'priority': 'HIGH',
                'min_strength': 0,
                'description': 'Portfolio risk limit exceeded'
            },
            'SECTOR_ROTATION': {
                'priority': 'MEDIUM',
                'min_strength': 60,
                'description': 'Sector rotation opportunity'
            }
        }

        # Load alert history
        self.alert_history = self.load_alert_history()

    def load_alert_history(self):
        """Load alert history from file"""
        try:
            with open('data/alert_history.json', 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {'alerts': [], 'daily_count': 0, 'last_reset': datetime.now().strftime('%Y-%m-%d')}

    def save_alert_history(self):
        """Save alert history to file"""
        try:
            # Ensure data directory exists
            os.makedirs('data', exist_ok=True)
            with open('data/alert_history.json', 'w') as f:
                json.dump(self.alert_history, f, indent=2, default=str)
        except Exception as e:
            print(f"Warning: Could not save alert history: {e}")

    def reset_daily_count_if_needed(self):
        """Reset daily alert count if new day"""
        today = datetime.now().strftime('%Y-%m-%d')
        if self.alert_history['last_reset'] != today:
            self.alert_history['daily_count'] = 0
            self.alert_history['last_reset'] = today

    def should_alert_symbol(self, symbol):
        """Check if we should alert for a symbol based on cooldown"""
        now = datetime.now()
        cutoff = now - timedelta(hours=self.alert_config['alert_cooldown_hours'])

        # Check recent alerts for this symbol
        for alert in self.alert_history['alerts']:
            if (alert['symbol'] == symbol and
                datetime.fromisoformat(alert['timestamp']) > cutoff):
                return False

        return True

    def can_send_more_alerts(self):
        """Check if we can send more alerts today"""
        self.reset_daily_count_if_needed()
        return self.alert_history['daily_count'] < self.alert_config['max_alerts_per_day']

    def detect_strong_buy_signals(self, symbols):
        """Detect strong buy signals across symbols"""
        alerts = []

        for symbol in symbols:
            if not self.should_alert_symbol(symbol):
                continue

            try:
                # Get smart money analysis
                analysis = self.analyzer.analyze_symbol(symbol, days_back=60)

                if 'error' in analysis:
                    continue

                signal_strength = analysis['market_context']['adjusted_score']

                if signal_strength >= self.alert_types['STRONG_BUY']['min_strength']:
                    # Additional validation
                    components = analysis['composite_score']['component_scores']

                    # Check for confluence of factors
                    strong_components = sum(1 for score in components.values() if score >= 65)

                    if strong_components >= 3:  # At least 3 strong components
                        alert = {
                            'type': 'STRONG_BUY',
                            'symbol': symbol,
                            'strength': signal_strength,
                            'confidence': min(signal_strength / 100, 1.0),
                            'components': components,
                            'message': f"{symbol}: Strong institutional buying detected (Score: {signal_strength:.1f})",
                            'recommendations': {
                                'action': 'Consider buying',
                                'urgency': 'High',
                                'position_size': '5-8% of portfolio',
                                'stop_loss': 'Set 8% below entry',
                                'take_profit': 'Target 15-20% gain'
                            }
                        }
                        alerts.append(alert)

            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                continue

        return alerts

    def detect_breakout_signals(self, symbols):
        """Detect breakout signals with volume confirmation"""
        alerts = []

        for symbol in symbols:
            if not self.should_alert_symbol(symbol):
                continue

            try:
                # Get recent price data (simplified for this system)
                with self.db.get_connection() as conn:
                    cursor = conn.execute("""
                        SELECT close, volume FROM price_data
                        WHERE stock_symbol = ?
                        ORDER BY date DESC
                        LIMIT 10
                    """, (symbol,))

                    data = cursor.fetchall()

                if len(data) < 5:
                    continue

                prices = [row[0] for row in data]
                volumes = [row[1] for row in data]

                current_price = prices[0]
                avg_price_5d = sum(prices[:5]) / 5
                current_volume = volumes[0]
                avg_volume_5d = sum(volumes[:5]) / 5

                # Check for breakout conditions
                price_breakout = (current_price - avg_price_5d) / avg_price_5d > self.alert_config['breakout_threshold']
                volume_surge = current_volume / avg_volume_5d > self.alert_config['volume_surge_threshold']

                if price_breakout and volume_surge:
                    # Get smart money confirmation
                    analysis = self.analyzer.analyze_symbol(symbol, days_back=30)

                    if 'error' not in analysis:
                        signal_strength = analysis['market_context']['adjusted_score']

                        if signal_strength >= self.alert_types['BREAKOUT_BUY']['min_strength']:
                            alert = {
                                'type': 'BREAKOUT_BUY',
                                'symbol': symbol,
                                'strength': signal_strength,
                                'price_change': (current_price - avg_price_5d) / avg_price_5d,
                                'volume_ratio': current_volume / avg_volume_5d,
                                'message': f"{symbol}: Bullish breakout with {volume_surge:.1f}x volume surge",
                                'recommendations': {
                                    'action': 'Consider buying on pullback',
                                    'urgency': 'Medium-High',
                                    'entry_strategy': 'Wait for slight pullback or buy momentum',
                                    'stop_loss': f"Below {avg_price_5d:.0f} VND",
                                    'target': f"Next resistance level"
                                }
                            }
                            alerts.append(alert)

            except Exception as e:
                print(f"Error analyzing breakout for {symbol}: {e}")
                continue

        return alerts

    def detect_risk_warnings(self):
        """Detect portfolio risk warnings"""
        alerts = []

        try:
            # Get current portfolio risk
            risk_assessment = self.risk_manager.assess_portfolio_risk()

            # Check overall portfolio risk
            if risk_assessment['total_risk'] > self.alert_config['max_portfolio_risk']:
                alert = {
                    'type': 'RISK_WARNING',
                    'symbol': 'PORTFOLIO',
                    'risk_level': risk_assessment['total_risk'],
                    'message': f"Portfolio risk ({risk_assessment['total_risk']:.1%}) exceeds limit",
                    'warnings': risk_assessment['warnings'],
                    'recommendations': {
                        'action': 'Reduce position sizes',
                        'urgency': 'High',
                        'specific_actions': [
                            'Consider reducing high-correlation positions',
                            'Rebalance sector allocations',
                            'Increase cash reserves'
                        ]
                    }
                }
                alerts.append(alert)

            # Check individual position risks
            for symbol, risk in risk_assessment['position_risks'].items():
                if risk > 0.08:  # 8% individual position risk
                    alert = {
                        'type': 'RISK_WARNING',
                        'symbol': symbol,
                        'risk_level': risk,
                        'message': f"{symbol} position risk ({risk:.1%}) is high",
                        'recommendations': {
                            'action': 'Consider reducing position size',
                            'urgency': 'Medium',
                            'target_risk': '5% or below'
                        }
                    }
                    alerts.append(alert)

        except Exception as e:
            print(f"Error in risk warning detection: {e}")

        return alerts

    def detect_sector_rotation(self, symbols):
        """Detect sector rotation opportunities"""
        alerts = []

        try:
            # Group symbols by sector and analyze performance
            db = self.db
            stocks = db.get_all_stocks()

            sector_performance = {}
            for stock in stocks:
                if stock['symbol'] not in symbols:
                    continue

                sector = stock['sector']
                if sector not in sector_performance:
                    sector_performance[sector] = {'symbols': [], 'scores': []}

                try:
                    analysis = self.analyzer.analyze_symbol(stock['symbol'], days_back=30)
                    if 'error' not in analysis:
                        score = analysis['market_context']['adjusted_score']
                        sector_performance[sector]['symbols'].append(stock['symbol'])
                        sector_performance[sector]['scores'].append(score)
                except:
                    continue

            # Calculate sector averages and identify rotation
            sector_averages = {}
            for sector, data in sector_performance.items():
                if data['scores']:
                    sector_averages[sector] = sum(data['scores']) / len(data['scores'])

            if len(sector_averages) >= 2:
                best_sector = max(sector_averages, key=sector_averages.get)
                worst_sector = min(sector_averages, key=sector_averages.get)

                score_diff = sector_averages[best_sector] - sector_averages[worst_sector]

                # Significant sector divergence
                if score_diff > 15:
                    alert = {
                        'type': 'SECTOR_ROTATION',
                        'symbol': 'MARKET',
                        'best_sector': best_sector,
                        'worst_sector': worst_sector,
                        'score_difference': score_diff,
                        'message': f"Sector rotation: {best_sector.title()} outperforming {worst_sector.title()}",
                        'recommendations': {
                            'action': f"Consider increasing {best_sector.title()} allocation",
                            'urgency': 'Medium',
                            'avoid_sector': worst_sector.title(),
                            'rotation_strength': 'Strong' if score_diff > 20 else 'Moderate'
                        }
                    }
                    alerts.append(alert)

        except Exception as e:
            print(f"Error in sector rotation detection: {e}")

        return alerts

    def process_alert(self, alert):
        """Process and format alert for delivery"""
        now = datetime.now()

        formatted_alert = {
            'id': f"{alert['symbol']}_{alert['type']}_{int(now.timestamp())}",
            'timestamp': now.isoformat(),
            'symbol': alert['symbol'],
            'type': alert['type'],
            'priority': self.alert_types[alert['type']]['priority'],
            'message': alert['message'],
            'data': alert,
            'recommendations': alert.get('recommendations', {}),
            'expiry': (now + timedelta(hours=4)).isoformat()  # Alert expires in 4 hours
        }

        return formatted_alert

    def send_alert(self, alert):
        """Send alert (placeholder for actual delivery mechanism)"""
        # In a real system, this would send emails, SMS, push notifications, etc.
        print(f"\n🚨 ALERT - {alert['priority']} PRIORITY")
        print(f"   Type: {alert['type']}")
        print(f"   Symbol: {alert['symbol']}")
        print(f"   Message: {alert['message']}")
        print(f"   Time: {alert['timestamp']}")

        if alert['recommendations']:
            print(f"   📋 Recommendations:")
            for key, value in alert['recommendations'].items():
                if isinstance(value, list):
                    print(f"     {key.title()}:")
                    for item in value:
                        print(f"       • {item}")
                else:
                    print(f"     {key.title()}: {value}")

        print("-" * 50)

        # Log alert
        self.alert_history['alerts'].append(alert)
        self.alert_history['daily_count'] += 1

        # Keep only last 100 alerts
        if len(self.alert_history['alerts']) > 100:
            self.alert_history['alerts'] = self.alert_history['alerts'][-100:]

        self.save_alert_history()

    def run_alert_scan(self, symbols=None):
        """Run comprehensive alert scan"""
        if not self.can_send_more_alerts():
            print("Daily alert limit reached")
            return []

        if symbols is None:
            stocks = self.db.get_all_stocks()
            symbols = [stock['symbol'] for stock in stocks]

        print(f"Running alert scan for {len(symbols)} symbols...")

        all_alerts = []

        # Detect different types of alerts
        try:
            # Strong buy signals
            strong_buy_alerts = self.detect_strong_buy_signals(symbols)
            all_alerts.extend(strong_buy_alerts)

            # Breakout signals
            breakout_alerts = self.detect_breakout_signals(symbols)
            all_alerts.extend(breakout_alerts)

            # Risk warnings
            risk_alerts = self.detect_risk_warnings()
            all_alerts.extend(risk_alerts)

            # Sector rotation
            sector_alerts = self.detect_sector_rotation(symbols)
            all_alerts.extend(sector_alerts)

        except Exception as e:
            print(f"Error during alert scan: {e}")

        # Process and send alerts
        sent_alerts = []
        for alert_data in all_alerts:
            if not self.can_send_more_alerts():
                break

            formatted_alert = self.process_alert(alert_data)
            self.send_alert(formatted_alert)
            sent_alerts.append(formatted_alert)

        print(f"Alert scan completed: {len(sent_alerts)} alerts sent")
        return sent_alerts

    def get_alert_summary(self):
        """Get summary of recent alerts"""
        now = datetime.now()
        recent_cutoff = now - timedelta(hours=24)

        recent_alerts = [
            alert for alert in self.alert_history['alerts']
            if datetime.fromisoformat(alert['timestamp']) > recent_cutoff
        ]

        summary = {
            'total_alerts_24h': len(recent_alerts),
            'alerts_by_type': {},
            'alerts_by_priority': {},
            'alerts_by_symbol': {},
            'daily_count': self.alert_history['daily_count'],
            'remaining_today': self.alert_config['max_alerts_per_day'] - self.alert_history['daily_count']
        }

        for alert in recent_alerts:
            # By type
            alert_type = alert['type']
            summary['alerts_by_type'][alert_type] = summary['alerts_by_type'].get(alert_type, 0) + 1

            # By priority
            priority = alert['priority']
            summary['alerts_by_priority'][priority] = summary['alerts_by_priority'].get(priority, 0) + 1

            # By symbol
            symbol = alert['symbol']
            summary['alerts_by_symbol'][symbol] = summary['alerts_by_symbol'].get(symbol, 0) + 1

        return summary

def main():
    """Test alert system"""
    print("Vietnam Stock Analysis - Automated Alert System")
    print("=" * 70)

    alert_system = VietnameseAlertSystem()

    try:
        print("Testing alert system with top Vietnamese stocks...")

        # Test with key stocks
        test_symbols = ['VCB', 'HPG', 'VHM', 'CTG', 'BID']

        # Run alert scan
        alerts = alert_system.run_alert_scan(test_symbols)

        print(f"\n📊 Alert Scan Results:")
        print(f"  Alerts Generated: {len(alerts)}")

        # Get alert summary
        summary = alert_system.get_alert_summary()

        print(f"\n📈 Alert Summary (24h):")
        print(f"  Total Alerts: {summary['total_alerts_24h']}")
        print(f"  Daily Count: {summary['daily_count']}/{alert_system.alert_config['max_alerts_per_day']}")

        if summary['alerts_by_type']:
            print(f"  By Type:")
            for alert_type, count in summary['alerts_by_type'].items():
                print(f"    {alert_type}: {count}")

        if summary['alerts_by_priority']:
            print(f"  By Priority:")
            for priority, count in summary['alerts_by_priority'].items():
                print(f"    {priority}: {count}")

        print(f"\n✅ Alert system test completed!")

        # System status
        print(f"\n🎯 Alert System Status:")
        print(f"  • Scan Frequency: {alert_system.alert_config['scan_frequency_minutes']} minutes")
        print(f"  • Min Signal Strength: {alert_system.alert_config['min_signal_strength']}")
        print(f"  • Min Confidence: {alert_system.alert_config['min_confidence']:.0%}")
        print(f"  • Alert Cooldown: {alert_system.alert_config['alert_cooldown_hours']} hours")
        print(f"  • Max Daily Alerts: {alert_system.alert_config['max_alerts_per_day']}")

    except Exception as e:
        print(f"❌ Alert system error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()