#!/usr/bin/env python3
"""
Alert System for Vietnam Stock Analysis
Monitors portfolio and generates email/SMS alerts for significant events
"""

import json
import pandas as pd
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VietnamStockAlerts:
    def __init__(self):
        self.alert_config = {
            'price_drop_threshold': -5.0,  # Alert if stock drops >5%
            'price_surge_threshold': 5.0,   # Alert if stock gains >5%
            'eic_change_threshold': 1.0,    # Alert if EIC score changes >1.0
            'volume_spike_threshold': 2.0,  # Alert if volume >200% of average
            'email_enabled': True,
            'sms_enabled': False  # Would need Twilio setup
        }

        # Sample portfolio (in real implementation, load from Google Sheets)
        self.portfolio = [
            {'symbol': 'VCB', 'quantity': 100, 'avg_price': 62700},
            {'symbol': 'SSI', 'quantity': 200, 'avg_price': 39900},
            {'symbol': 'HPG', 'quantity': 150, 'avg_price': 28500}
        ]

    def load_latest_data(self):
        """Load the latest stock data from daily collection"""
        try:
            # Find the most recent data file
            import glob
            data_files = glob.glob('/workspaces/BMAD-METHOD/session_logs/daily_stock_data_*.json')

            if not data_files:
                logging.error("No data files found")
                return None

            latest_file = max(data_files)

            with open(latest_file, 'r') as f:
                data = json.load(f)

            logging.info(f"Loaded data from {latest_file}")
            return data

        except Exception as e:
            logging.error(f"Error loading data: {e}")
            return None

    def check_price_alerts(self, current_data):
        """Check for significant price movements"""
        alerts = []

        for stock in current_data:
            symbol = stock['symbol']
            change_pct = stock['change_pct']
            current_price = stock['current_price']

            # Check if this stock is in portfolio
            portfolio_stock = next((p for p in self.portfolio if p['symbol'] == symbol), None)

            # Price drop alert
            if change_pct <= self.alert_config['price_drop_threshold']:
                severity = 'HIGH' if change_pct <= -7 else 'MEDIUM'

                alert = {
                    'type': 'PRICE_DROP',
                    'symbol': symbol,
                    'current_price': current_price,
                    'change_pct': change_pct,
                    'message': f"{symbol} dropped {change_pct:.2f}% today",
                    'severity': severity,
                    'portfolio_impact': self.calculate_portfolio_impact(portfolio_stock, change_pct) if portfolio_stock else None,
                    'recommendation': self.get_price_drop_recommendation(stock),
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)

            # Price surge alert
            elif change_pct >= self.alert_config['price_surge_threshold']:
                severity = 'MEDIUM' if change_pct >= 7 else 'LOW'

                alert = {
                    'type': 'PRICE_SURGE',
                    'symbol': symbol,
                    'current_price': current_price,
                    'change_pct': change_pct,
                    'message': f"{symbol} surged {change_pct:.2f}% today",
                    'severity': severity,
                    'portfolio_impact': self.calculate_portfolio_impact(portfolio_stock, change_pct) if portfolio_stock else None,
                    'recommendation': self.get_price_surge_recommendation(stock),
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)

        return alerts

    def check_eic_alerts(self, current_data):
        """Check for significant EIC score changes"""
        alerts = []

        # In real implementation, compare with previous day's EIC scores
        # For demo, simulate some EIC changes

        for stock in current_data:
            # Simulate previous EIC score (would load from historical data)
            previous_eic = stock['eic_score'] - 0.3  # Simulate slight decrease
            current_eic = stock['eic_score']
            eic_change = current_eic - previous_eic

            if abs(eic_change) >= self.alert_config['eic_change_threshold']:
                portfolio_stock = next((p for p in self.portfolio if p['symbol'] == stock['symbol']), None)

                alert_type = 'EIC_UPGRADE' if eic_change > 0 else 'EIC_DOWNGRADE'
                severity = 'HIGH' if abs(eic_change) >= 1.5 else 'MEDIUM'

                alert = {
                    'type': alert_type,
                    'symbol': stock['symbol'],
                    'previous_eic': previous_eic,
                    'current_eic': current_eic,
                    'eic_change': eic_change,
                    'message': f"{stock['symbol']} EIC score changed from {previous_eic:.1f} to {current_eic:.1f}",
                    'severity': severity,
                    'new_signal': stock['signal'],
                    'recommendation': self.get_eic_recommendation(stock, eic_change),
                    'portfolio_held': portfolio_stock is not None,
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)

        return alerts

    def check_volume_alerts(self, current_data):
        """Check for unusual volume spikes"""
        alerts = []

        for stock in current_data:
            if 'volume_ratio' in stock and stock['volume_ratio'] >= self.alert_config['volume_spike_threshold']:

                alert = {
                    'type': 'VOLUME_SPIKE',
                    'symbol': stock['symbol'],
                    'current_volume': stock['volume'],
                    'volume_ratio': stock['volume_ratio'],
                    'message': f"{stock['symbol']} volume {stock['volume_ratio']:.1f}x higher than average",
                    'severity': 'MEDIUM',
                    'possible_causes': self.analyze_volume_spike(stock),
                    'recommendation': "Monitor for news or announcements",
                    'timestamp': datetime.now().isoformat()
                }
                alerts.append(alert)

        return alerts

    def calculate_portfolio_impact(self, portfolio_stock, change_pct):
        """Calculate P&L impact on portfolio position"""
        if not portfolio_stock:
            return None

        position_value = portfolio_stock['quantity'] * portfolio_stock['avg_price']
        impact_amount = position_value * (change_pct / 100)

        return {
            'position_value': position_value,
            'impact_amount': impact_amount,
            'impact_pct': change_pct
        }

    def get_price_drop_recommendation(self, stock):
        """Generate recommendation for price drops"""
        eic_score = stock['eic_score']
        change_pct = stock['change_pct']

        if eic_score >= 7 and change_pct <= -5:
            return "Strong fundamentals - consider buying the dip"
        elif eic_score >= 6 and change_pct <= -3:
            return "Good fundamentals - monitor for further weakness"
        elif eic_score < 5:
            return "Weak fundamentals - consider reducing position"
        else:
            return "Monitor situation and wait for stabilization"

    def get_price_surge_recommendation(self, stock):
        """Generate recommendation for price surges"""
        eic_score = stock['eic_score']
        change_pct = stock['change_pct']

        if eic_score >= 7 and change_pct >= 5:
            return "Strong momentum with good fundamentals - consider holding"
        elif change_pct >= 10:
            return "Large gain - consider taking partial profits"
        else:
            return "Monitor for continuation or reversal"

    def get_eic_recommendation(self, stock, eic_change):
        """Generate recommendation for EIC changes"""
        current_eic = stock['eic_score']

        if eic_change > 0:
            if current_eic >= 7:
                return "Upgrade to strong fundamentals - consider increasing position"
            else:
                return "Improving fundamentals - add to watchlist"
        else:
            if current_eic < 5:
                return "Deteriorating fundamentals - consider reducing position"
            else:
                return "Slight weakness - monitor closely"

    def analyze_volume_spike(self, stock):
        """Analyze possible causes of volume spikes"""
        change_pct = stock['change_pct']

        causes = []

        if abs(change_pct) > 3:
            causes.append("Significant price movement")
        if stock['volume_ratio'] > 3:
            causes.append("Possible news announcement")
        if stock['eic_score'] >= 7:
            causes.append("Strong fundamentals attracting attention")

        return causes if causes else ["Unknown catalyst"]

    def format_alert_email(self, alerts):
        """Format alerts into HTML email"""
        if not alerts:
            return None

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .header {{ background-color: #1e3a8a; color: white; padding: 20px; text-align: center; }}
                .alert {{ margin: 15px 0; padding: 15px; border-left: 5px solid; }}
                .high {{ border-color: #dc2626; background-color: #fef2f2; }}
                .medium {{ border-color: #f59e0b; background-color: #fffbeb; }}
                .low {{ border-color: #10b981; background-color: #f0fdf4; }}
                .portfolio {{ background-color: #e0f2fe; padding: 10px; margin: 10px 0; }}
                .recommendation {{ font-weight: bold; color: #1e40af; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>Vietnam Stock Analysis - Alert Report</h2>
                <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>

            <h3>Active Alerts ({len(alerts)})</h3>
        """

        for alert in alerts:
            severity_class = alert['severity'].lower()

            html += f"""
            <div class="alert {severity_class}">
                <h4>{alert['type'].replace('_', ' ').title()}: {alert['symbol']}</h4>
                <p><strong>Message:</strong> {alert['message']}</p>
            """

            if alert['type'] in ['PRICE_DROP', 'PRICE_SURGE']:
                html += f"<p><strong>Current Price:</strong> {alert['current_price']:,.0f} VND</p>"

                if alert.get('portfolio_impact'):
                    impact = alert['portfolio_impact']
                    html += f"""
                    <div class="portfolio">
                        <strong>Portfolio Impact:</strong><br>
                        Position Value: {impact['position_value']:,.0f} VND<br>
                        P&L Impact: {impact['impact_amount']:+,.0f} VND ({impact['impact_pct']:+.2f}%)
                    </div>
                    """

            elif alert['type'] in ['EIC_UPGRADE', 'EIC_DOWNGRADE']:
                html += f"""
                <p><strong>EIC Change:</strong> {alert['previous_eic']:.1f} → {alert['current_eic']:.1f}</p>
                <p><strong>New Signal:</strong> {alert['new_signal']}</p>
                """

            html += f'<p class="recommendation">Recommendation: {alert["recommendation"]}</p>'
            html += "</div>"

        html += """
            <hr>
            <p><em>This is an automated alert from your Vietnam Stock Analysis System</em></p>
        </body>
        </html>
        """

        return html

    def send_email_alert(self, alerts):
        """Send email alerts (placeholder - requires email setup)"""
        if not alerts or not self.alert_config['email_enabled']:
            return False

        email_html = self.format_alert_email(alerts)

        # Email configuration (would need actual SMTP settings)
        email_config = {
            'smtp_server': 'smtp.gmail.com',  # Replace with your SMTP server
            'smtp_port': 587,
            'email': 'your-email@gmail.com',   # Replace with your email
            'password': 'your-app-password',   # Replace with app password
            'to_email': 'your-email@gmail.com'  # Replace with your email
        }

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Vietnam Stock Alerts - {len(alerts)} alerts"
            msg['From'] = email_config['email']
            msg['To'] = email_config['to_email']

            # Add HTML content
            html_part = MIMEText(email_html, 'html')
            msg.attach(html_part)

            # Note: This would actually send email if configured
            logging.info(f"Email alert prepared for {len(alerts)} alerts")
            logging.info("Email sending disabled - configure SMTP settings to enable")

            # Uncomment below to actually send emails (after configuring SMTP)
            # server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            # server.starttls()
            # server.login(email_config['email'], email_config['password'])
            # server.send_message(msg)
            # server.quit()

            return True

        except Exception as e:
            logging.error(f"Error sending email: {e}")
            return False

    def save_alerts(self, alerts):
        """Save alerts to file for dashboard display"""
        if not alerts:
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        alerts_file = f'/workspaces/BMAD-METHOD/session_logs/alerts_{timestamp}.json'

        # Add alert metadata
        alert_summary = {
            'timestamp': datetime.now().isoformat(),
            'total_alerts': len(alerts),
            'high_priority': len([a for a in alerts if a['severity'] == 'HIGH']),
            'medium_priority': len([a for a in alerts if a['severity'] == 'MEDIUM']),
            'low_priority': len([a for a in alerts if a['severity'] == 'LOW']),
            'alerts': alerts
        }

        with open(alerts_file, 'w') as f:
            json.dump(alert_summary, f, indent=2, default=str)

        logging.info(f"Saved {len(alerts)} alerts to {alerts_file}")

        # Also save in CSV format for Google Sheets
        alerts_df = pd.DataFrame(alerts)
        csv_file = f'/workspaces/BMAD-METHOD/session_logs/alerts_{timestamp}.csv'
        alerts_df.to_csv(csv_file, index=False)

        return alerts_file

    def run_alert_check(self):
        """Main method to check all alerts"""
        logging.info("="*50)
        logging.info("VIETNAM STOCK ALERTS - CHECKING")
        logging.info("="*50)

        # Load latest data
        current_data = self.load_latest_data()
        if not current_data:
            logging.error("No data available for alert checking")
            return False

        # Check all alert types
        all_alerts = []

        # Price alerts
        price_alerts = self.check_price_alerts(current_data)
        all_alerts.extend(price_alerts)
        logging.info(f"Price alerts: {len(price_alerts)}")

        # EIC alerts
        eic_alerts = self.check_eic_alerts(current_data)
        all_alerts.extend(eic_alerts)
        logging.info(f"EIC alerts: {len(eic_alerts)}")

        # Volume alerts
        volume_alerts = self.check_volume_alerts(current_data)
        all_alerts.extend(volume_alerts)
        logging.info(f"Volume alerts: {len(volume_alerts)}")

        # Process alerts
        if all_alerts:
            logging.info(f"Total alerts generated: {len(all_alerts)}")

            # Save alerts
            self.save_alerts(all_alerts)

            # Send notifications
            self.send_email_alert(all_alerts)

            # Print summary
            for alert in all_alerts:
                logging.info(f"{alert['severity']} - {alert['symbol']}: {alert['message']}")

        else:
            logging.info("No alerts generated - all stocks within normal ranges")

        return True

    def create_test_alerts(self):
        """Create test alerts for demonstration"""
        test_alerts = [
            {
                'type': 'PRICE_DROP',
                'symbol': 'VHM',
                'current_price': 104000,
                'change_pct': -0.95,
                'message': 'VHM dropped 0.95% today',
                'severity': 'LOW',
                'recommendation': 'Monitor situation and wait for stabilization',
                'timestamp': datetime.now().isoformat()
            },
            {
                'type': 'VOLUME_SPIKE',
                'symbol': 'BID',
                'current_volume': 2100000,
                'volume_ratio': 2.4,
                'message': 'BID volume 2.4x higher than average',
                'severity': 'MEDIUM',
                'recommendation': 'Monitor for news or announcements',
                'timestamp': datetime.now().isoformat()
            }
        ]

        logging.info("Creating test alerts for demonstration")
        self.save_alerts(test_alerts)
        email_html = self.format_alert_email(test_alerts)

        # Save email preview
        with open('/workspaces/BMAD-METHOD/session_logs/alert_email_preview.html', 'w') as f:
            f.write(email_html)

        logging.info("Test alerts created and email preview saved")
        return test_alerts

if __name__ == "__main__":
    alert_system = VietnamStockAlerts()

    # Run real alert check
    alert_system.run_alert_check()

    # Also create test alerts for demonstration
    alert_system.create_test_alerts()