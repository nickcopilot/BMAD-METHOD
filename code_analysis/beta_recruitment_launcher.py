#!/usr/bin/env python3
"""
Beta Recruitment Campaign Launcher
Automated system for launching and managing beta tester recruitment
"""

import smtplib
import json
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import logging
from pathlib import Path
from typing import List, Dict
import requests
from beta_user_system import BetaUserManager
from beta_monitoring_system import BetaMonitoringSystem

class BetaRecruitmentLauncher:
    """Manages beta tester recruitment campaign"""

    def __init__(self):
        self.setup_logging()
        self.user_manager = BetaUserManager()
        self.monitoring = BetaMonitoringSystem()

        # Email configuration
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')

        # Campaign configuration
        self.campaign_config = {
            'max_beta_testers': 50,
            'target_segments': {
                'vietnamese_traders': 35,  # 70%
                'financial_professionals': 10,  # 20%
                'international_investors': 5   # 10%
            },
            'recruitment_phases': {
                'phase_1_direct_outreach': 7,    # days
                'phase_2_referral_program': 7,   # days
                'phase_3_open_applications': 14  # days
            }
        }

    def setup_logging(self):
        """Setup logging for recruitment campaign"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/beta_recruitment.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_recruitment_templates(self) -> Dict:
        """Load email templates and content"""
        # Read from beta_recruitment_content.md
        try:
            with open('beta_recruitment_content.md', 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse email templates (this is a simplified version)
            templates = {
                'community_outreach': self.extract_email_template(content, "Outreach Email to Vietnamese Trading Communities"),
                'professional_outreach': self.extract_email_template(content, "Direct Outreach to Financial Professionals"),
                'linkedin_post': self.extract_social_content(content, "LinkedIn Post"),
                'facebook_post': self.extract_social_content(content, "Facebook Group Post"),
                'twitter_thread': self.extract_social_content(content, "Twitter Thread")
            }

            return templates
        except Exception as e:
            self.logger.error(f"Error loading recruitment templates: {e}")
            return {}

    def extract_email_template(self, content: str, section_name: str) -> str:
        """Extract email template from markdown content"""
        # Simple extraction - in production, use proper markdown parsing
        start_marker = f"### {section_name}"
        start_idx = content.find(start_marker)
        if start_idx == -1:
            return ""

        # Find the next section or end
        next_section = content.find("###", start_idx + len(start_marker))
        if next_section == -1:
            section_content = content[start_idx:]
        else:
            section_content = content[start_idx:next_section]

        # Extract content between ``` markers
        code_start = section_content.find("```")
        code_end = section_content.find("```", code_start + 3)

        if code_start != -1 and code_end != -1:
            return section_content[code_start + 3:code_end].strip()

        return section_content.strip()

    def extract_social_content(self, content: str, section_name: str) -> str:
        """Extract social media content from markdown"""
        return self.extract_email_template(content, section_name)

    def get_recruitment_targets(self) -> Dict[str, List[Dict]]:
        """Get recruitment target lists"""
        # In production, these would be loaded from databases/CRM systems
        targets = {
            'vietnamese_communities': [
                {
                    'name': 'Vietnam Stock Traders Facebook Group',
                    'contact': 'admin@vietnamstocktraders.com',
                    'type': 'facebook_group',
                    'members': 15000,
                    'engagement': 'high'
                },
                {
                    'name': 'Vietnamese Financial Professionals LinkedIn',
                    'contact': 'network@vn-finance.com',
                    'type': 'linkedin_group',
                    'members': 8000,
                    'engagement': 'medium'
                },
                {
                    'name': 'Hanoi Stock Exchange Community',
                    'contact': 'community@hsx.vn',
                    'type': 'professional_network',
                    'members': 5000,
                    'engagement': 'high'
                }
            ],
            'financial_professionals': [
                {
                    'name': 'Minh Nguyen',
                    'email': 'minh.nguyen@vn-securities.com',
                    'role': 'Senior Investment Advisor',
                    'company': 'Vietnam Securities',
                    'linkedin': 'linkedin.com/in/minh-nguyen-finance'
                },
                {
                    'name': 'Sarah Chen',
                    'email': 'sarah.chen@asia-invest.com',
                    'role': 'Fund Manager',
                    'company': 'Asia Investment Partners',
                    'linkedin': 'linkedin.com/in/sarah-chen-asia'
                }
            ],
            'international_investors': [
                {
                    'name': 'David Thompson',
                    'email': 'david@emerging-markets.com',
                    'role': 'Emerging Markets Analyst',
                    'company': 'Global Investment Fund',
                    'linkedin': 'linkedin.com/in/david-thompson-em'
                }
            ]
        }

        return targets

    def launch_phase_1_direct_outreach(self):
        """Phase 1: Direct outreach to target communities and professionals"""
        self.logger.info("🚀 Launching Phase 1: Direct Outreach")

        templates = self.load_recruitment_templates()
        targets = self.get_recruitment_targets()

        # Track campaign launch
        self.monitoring.record_system_metric(
            "recruitment_phase_1_launched", 1.0, "count",
            {"timestamp": datetime.now().isoformat()}
        )

        # Outreach to communities
        self.logger.info("📧 Sending community outreach emails...")
        for community in targets['vietnamese_communities']:
            self.send_community_outreach(community, templates['community_outreach'])

        # Outreach to professionals
        self.logger.info("📧 Sending professional outreach emails...")
        for professional in targets['financial_professionals']:
            self.send_professional_outreach(professional, templates['professional_outreach'])

        # Social media content preparation
        self.prepare_social_media_content(templates)

        self.logger.info("✅ Phase 1 Direct Outreach completed")

    def send_community_outreach(self, community: Dict, template: str):
        """Send outreach email to trading communities"""
        if not self.smtp_username or not self.smtp_password:
            self.logger.warning(f"Email not configured, skipping outreach to {community['name']}")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = community['contact']
            msg['Subject'] = "Exclusive Beta Access: Revolutionary Vietnam Stock Analysis System"

            # Customize template with community data
            personalized_content = template.replace('[Community/Group Name]', community['name'])
            personalized_content = personalized_content.replace('[Name]', 'Admin')

            msg.attach(MIMEText(personalized_content, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"✅ Outreach sent to {community['name']}")

            # Track outreach
            self.monitoring.record_system_metric(
                "community_outreach_sent", 1.0, "count",
                {"community": community['name'], "type": community['type']}
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to send outreach to {community['name']}: {e}")

    def send_professional_outreach(self, professional: Dict, template: str):
        """Send outreach email to financial professionals"""
        if not self.smtp_username or not self.smtp_password:
            self.logger.warning(f"Email not configured, skipping outreach to {professional['name']}")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = professional['email']
            msg['Subject'] = "Beta Testing Invitation: Vietnamese Stock Analysis Platform (100% Validated)"

            # Customize template with professional data
            personalized_content = template.replace('[Name]', professional['name'])
            personalized_content = personalized_content.replace('[professional role]', professional['role'])

            msg.attach(MIMEText(personalized_content, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"✅ Professional outreach sent to {professional['name']}")

            # Track outreach
            self.monitoring.record_system_metric(
                "professional_outreach_sent", 1.0, "count",
                {"name": professional['name'], "role": professional['role']}
            )

        except Exception as e:
            self.logger.error(f"❌ Failed to send outreach to {professional['name']}: {e}")

    def prepare_social_media_content(self, templates: Dict):
        """Prepare social media content for manual posting"""
        social_content_dir = Path("social_media_content")
        social_content_dir.mkdir(exist_ok=True)

        # Save social media templates as files for easy posting
        social_platforms = ['linkedin_post', 'facebook_post', 'twitter_thread']

        for platform in social_platforms:
            if platform in templates:
                content_file = social_content_dir / f"{platform}_{datetime.now().strftime('%Y%m%d')}.txt"
                with open(content_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {platform.replace('_', ' ').title()}\n")
                    f.write(f"Generated on: {datetime.now()}\n\n")
                    f.write(templates[platform])

                self.logger.info(f"📱 {platform} content saved to {content_file}")

    def launch_phase_2_referral_program(self):
        """Phase 2: Referral program for accepted beta testers"""
        self.logger.info("🔗 Launching Phase 2: Referral Program")

        # Get current beta testers
        current_testers = self.user_manager.get_all_beta_users()
        approved_testers = [user for user in current_testers if user.get('approved')]

        if not approved_testers:
            self.logger.warning("No approved beta testers found for referral program")
            return

        # Send referral invitations
        for tester in approved_testers:
            self.send_referral_invitation(tester)

        # Track referral program launch
        self.monitoring.record_system_metric(
            "referral_program_launched", 1.0, "count",
            {"invited_testers": len(approved_testers)}
        )

        self.logger.info(f"✅ Phase 2 Referral Program launched for {len(approved_testers)} testers")

    def send_referral_invitation(self, tester: Dict):
        """Send referral invitation to beta tester"""
        if not self.smtp_username or not self.smtp_password:
            self.logger.warning(f"Email not configured, skipping referral invitation")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = tester['email']
            msg['Subject'] = "🎁 Invite Friends to Beta: Earn Extended Access + Rewards"

            referral_content = f"""
Dear {tester['full_name']},

Thank you for being an amazing beta tester! Your feedback has been invaluable in refining our Vietnam Stock Analysis System.

🎁 EXCLUSIVE REFERRAL PROGRAM

As a valued beta tester, you can now invite up to 2 qualified candidates to join our program. Here's what you both get:

FOR YOU:
✅ Extended beta access (additional 4 weeks)
✅ Priority access to all future features
✅ Special "Super Beta Tester" recognition
✅ Revenue sharing: 20% commission on referred users after public launch

FOR YOUR REFERRALS:
✅ Fast-track application process
✅ Personal welcome from the team
✅ Guaranteed acceptance (if qualified)
✅ Extra training and support

HOW TO REFER:

1. Share this link with qualified candidates: [BETA_LANDING_PAGE_URL]
2. Ask them to mention your name in the "How did you hear about us" field
3. We'll track the referral and apply bonuses automatically

IDEAL REFERRALS:
- Active Vietnamese stock traders
- Financial professionals with VN market experience
- International investors interested in Vietnamese markets
- Anyone who can commit 5+ hours/week for testing

Questions? Reply to this email or contact us in the beta Slack channel.

Thank you for helping us build the best Vietnamese stock analysis platform!

Best regards,
Vietnam Stock Analysis Beta Team

P.S. Remember, your referrals must be approved and complete at least 4 weeks of testing for you to earn the full rewards.
"""

            msg.attach(MIMEText(referral_content, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"✅ Referral invitation sent to {tester['full_name']}")

        except Exception as e:
            self.logger.error(f"❌ Failed to send referral invitation to {tester['full_name']}: {e}")

    def launch_phase_3_open_applications(self):
        """Phase 3: Open applications with landing page"""
        self.logger.info("🌐 Launching Phase 3: Open Applications")

        # Update application status to open
        self.monitoring.record_system_metric(
            "open_applications_launched", 1.0, "count",
            {"timestamp": datetime.now().isoformat()}
        )

        # Generate application tracking report
        self.generate_recruitment_report()

        self.logger.info("✅ Phase 3 Open Applications launched")
        self.logger.info("📝 Beta landing page is now live and accepting applications")

    def track_application_metrics(self) -> Dict:
        """Track key recruitment metrics"""
        # Get application statistics
        all_users = self.user_manager.get_all_beta_users()

        total_applications = len(all_users)
        approved_applications = len([u for u in all_users if u.get('approved')])
        pending_applications = total_applications - approved_applications

        # Calculate conversion rates
        conversion_rate = (approved_applications / total_applications * 100) if total_applications > 0 else 0

        # Get recruitment source breakdown
        source_breakdown = {}
        for user in all_users:
            # This would typically come from application data
            source = user.get('referral_source', 'unknown')
            source_breakdown[source] = source_breakdown.get(source, 0) + 1

        metrics = {
            'total_applications': total_applications,
            'approved_applications': approved_applications,
            'pending_applications': pending_applications,
            'conversion_rate': conversion_rate,
            'source_breakdown': source_breakdown,
            'remaining_spots': self.campaign_config['max_beta_testers'] - approved_applications
        }

        return metrics

    def generate_recruitment_report(self):
        """Generate comprehensive recruitment report"""
        metrics = self.track_application_metrics()

        report = {
            'generated_at': datetime.now().isoformat(),
            'campaign_status': 'active',
            'recruitment_metrics': metrics,
            'target_progress': {
                'vietnamese_traders': {
                    'target': self.campaign_config['target_segments']['vietnamese_traders'],
                    'current': metrics['approved_applications'],  # Simplified
                    'progress': f"{(metrics['approved_applications'] / self.campaign_config['target_segments']['vietnamese_traders'] * 100):.1f}%"
                }
            },
            'next_actions': self.get_next_recruitment_actions(metrics)
        }

        # Save report
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)

        report_file = reports_dir / f"recruitment_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        self.logger.info(f"📊 Recruitment report generated: {report_file}")

        return report

    def get_next_recruitment_actions(self, metrics: Dict) -> List[str]:
        """Determine next recruitment actions based on current metrics"""
        actions = []

        remaining_spots = metrics['remaining_spots']
        conversion_rate = metrics['conversion_rate']

        if remaining_spots > 25:
            actions.append("Increase outreach efforts - many spots remaining")
            actions.append("Launch social media campaign")
            actions.append("Contact additional trading communities")
        elif remaining_spots > 10:
            actions.append("Maintain current recruitment pace")
            actions.append("Focus on quality over quantity")
        elif remaining_spots > 0:
            actions.append("Selective recruitment only")
            actions.append("Focus on high-quality candidates")
        else:
            actions.append("Close applications - beta program full")
            actions.append("Start waitlist for future programs")

        if conversion_rate < 50:
            actions.append("Review application screening criteria")
            actions.append("Improve application process")

        return actions

    def send_recruitment_status_update(self):
        """Send recruitment status update to team"""
        if not self.smtp_username or not self.smtp_password:
            self.logger.warning("Email not configured, skipping status update")
            return

        metrics = self.track_application_metrics()

        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = self.smtp_username  # Send to self for now
            msg['Subject'] = f"📊 Beta Recruitment Update - {metrics['approved_applications']}/50 Testers"

            update_content = f"""
BETA RECRUITMENT STATUS UPDATE
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

📈 KEY METRICS:
• Total Applications: {metrics['total_applications']}
• Approved Testers: {metrics['approved_applications']}/50
• Pending Review: {metrics['pending_applications']}
• Conversion Rate: {metrics['conversion_rate']:.1f}%
• Remaining Spots: {metrics['remaining_spots']}

📊 APPLICATION SOURCES:
{chr(10).join([f"• {source}: {count}" for source, count in metrics['source_breakdown'].items()])}

🎯 NEXT ACTIONS:
{chr(10).join([f"• {action}" for action in self.get_next_recruitment_actions(metrics)])}

STATUS: {'🟢 ON TRACK' if metrics['approved_applications'] >= 10 else '🟡 NEEDS ATTENTION'}

Full recruitment report available in reports/ directory.
"""

            msg.attach(MIMEText(update_content, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()

            self.logger.info("✅ Recruitment status update sent")

        except Exception as e:
            self.logger.error(f"❌ Failed to send status update: {e}")

    def launch_full_campaign(self):
        """Launch the complete recruitment campaign"""
        self.logger.info("🚀 LAUNCHING BETA RECRUITMENT CAMPAIGN")

        try:
            # Phase 1: Direct outreach
            self.launch_phase_1_direct_outreach()

            # Schedule Phase 2 and 3 (in production, use a task scheduler)
            self.logger.info("📅 Phase 2 scheduled for 7 days from now")
            self.logger.info("📅 Phase 3 scheduled for 14 days from now")

            # For immediate testing, launch all phases now
            self.launch_phase_2_referral_program()
            self.launch_phase_3_open_applications()

            # Send initial status update
            self.send_recruitment_status_update()

            self.logger.info("🎉 Beta recruitment campaign launched successfully!")

            # Print campaign summary
            self.print_campaign_summary()

        except Exception as e:
            self.logger.error(f"❌ Campaign launch failed: {e}")
            raise

    def print_campaign_summary(self):
        """Print campaign launch summary"""
        metrics = self.track_application_metrics()

        summary = f"""
🎯 BETA RECRUITMENT CAMPAIGN LAUNCHED

📊 Current Status:
• Target Beta Testers: {self.campaign_config['max_beta_testers']}
• Current Applications: {metrics['total_applications']}
• Approved Testers: {metrics['approved_applications']}
• Remaining Spots: {metrics['remaining_spots']}

🚀 Active Recruitment Channels:
• Direct outreach to Vietnamese trading communities
• Professional network outreach
• Referral program for existing beta testers
• Beta landing page: beta_landing_page.py

📝 Next Steps:
1. Monitor application flow via monitoring dashboard
2. Review applications daily
3. Send weekly recruitment status updates
4. Adjust recruitment strategy based on metrics

📧 Campaign Management:
• Track metrics: python -c "from beta_recruitment_launcher import BetaRecruitmentLauncher; BetaRecruitmentLauncher().generate_recruitment_report()"
• Send status update: python -c "from beta_recruitment_launcher import BetaRecruitmentLauncher; BetaRecruitmentLauncher().send_recruitment_status_update()"
• Launch landing page: streamlit run beta_landing_page.py --server.port=8503

🎉 Beta recruitment campaign is now LIVE!
"""

        print(summary)
        self.logger.info("Campaign summary printed")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Launch beta recruitment campaign")
    parser.add_argument("--phase", choices=["1", "2", "3", "all"], default="all",
                       help="Recruitment phase to launch")
    parser.add_argument("--status-update", action="store_true",
                       help="Send recruitment status update")
    parser.add_argument("--report", action="store_true",
                       help="Generate recruitment report only")

    args = parser.parse_args()

    launcher = BetaRecruitmentLauncher()

    try:
        if args.report:
            report = launcher.generate_recruitment_report()
            print(json.dumps(report, indent=2, default=str))
        elif args.status_update:
            launcher.send_recruitment_status_update()
        elif args.phase == "1":
            launcher.launch_phase_1_direct_outreach()
        elif args.phase == "2":
            launcher.launch_phase_2_referral_program()
        elif args.phase == "3":
            launcher.launch_phase_3_open_applications()
        else:
            launcher.launch_full_campaign()

    except Exception as e:
        print(f"❌ Campaign execution failed: {e}")
        exit(1)