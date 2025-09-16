#!/usr/bin/env python3
"""
Beta Environment Deployment Script
Automated deployment of the Vietnam Stock Analysis System for beta testing
"""

import os
import subprocess
import sqlite3
import json
import secrets
from pathlib import Path
from datetime import datetime
import logging
import sys

class BetaEnvironmentDeployer:
    """Handles automated deployment of beta testing environment"""

    def __init__(self, environment: str = "beta"):
        self.environment = environment
        self.base_dir = Path.cwd()
        self.setup_logging()
        self.config = self.load_deployment_config()

    def setup_logging(self):
        """Setup deployment logging"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'logs/beta_deployment_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def load_deployment_config(self) -> dict:
        """Load deployment configuration"""
        return {
            "beta": {
                "port": 8502,
                "database": "beta_vietnam_stocks.db",
                "max_users": 50,
                "features": {
                    "user_authentication": True,
                    "feedback_collection": True,
                    "performance_monitoring": True,
                    "beta_features": True
                }
            },
            "production": {
                "port": 8501,
                "database": "vietnam_stocks.db",
                "max_users": 1000,
                "features": {
                    "user_authentication": True,
                    "feedback_collection": False,
                    "performance_monitoring": True,
                    "beta_features": False
                }
            }
        }

    def check_prerequisites(self) -> bool:
        """Check if all prerequisites are met"""
        self.logger.info("Checking deployment prerequisites...")

        requirements = [
            ("Python 3.9+", self.check_python_version),
            ("Required packages", self.check_packages),
            ("Database directory", self.check_database_dir),
            ("Logs directory", self.check_logs_dir),
            ("Required files", self.check_required_files)
        ]

        all_passed = True
        for requirement, check_func in requirements:
            try:
                if check_func():
                    self.logger.info(f"✅ {requirement}: OK")
                else:
                    self.logger.error(f"❌ {requirement}: FAILED")
                    all_passed = False
            except Exception as e:
                self.logger.error(f"❌ {requirement}: ERROR - {e}")
                all_passed = False

        return all_passed

    def check_python_version(self) -> bool:
        """Check Python version"""
        return sys.version_info >= (3, 9)

    def check_packages(self) -> bool:
        """Check if required packages are installed"""
        required_packages = [
            'streamlit', 'pandas', 'numpy', 'plotly', 'vnstock',
            'sklearn', 'schedule'  # Note: sqlite3 is built-in, sklearn is the import name for scikit-learn
        ]

        missing_packages = []
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            self.logger.warning(f"Missing packages: {missing_packages}")
            return False
        return True

    def check_database_dir(self) -> bool:
        """Check if data directory exists"""
        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        return data_dir.exists()

    def check_logs_dir(self) -> bool:
        """Check if logs directory exists"""
        logs_dir = Path("logs")
        logs_dir.mkdir(exist_ok=True)
        return logs_dir.exists()

    def check_required_files(self) -> bool:
        """Check if all required files exist"""
        required_files = [
            "production_web_app.py",
            "smart_money_signal_system.py",
            "data_pipeline.py",
            "beta_user_system.py",
            "beta_monitoring_system.py"
        ]

        missing_files = []
        for file in required_files:
            if not Path(file).exists():
                missing_files.append(file)

        if missing_files:
            self.logger.error(f"Missing required files: {missing_files}")
            return False
        return True

    def install_dependencies(self):
        """Install required Python packages"""
        self.logger.info("Installing dependencies...")

        requirements = [
            "streamlit>=1.28.0",
            "pandas>=1.5.0",
            "numpy>=1.24.0",
            "plotly>=5.15.0",
            "vnstock>=0.2.8.2",
            "scikit-learn>=1.3.0",
            "schedule>=1.2.0",
            "python-dotenv>=1.0.0",
            "bcrypt>=4.0.0"
        ]

        try:
            for package in requirements:
                subprocess.run([sys.executable, "-m", "pip", "install", package],
                             check=True, capture_output=True)
            self.logger.info("✅ Dependencies installed successfully")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"❌ Failed to install dependencies: {e}")
            raise

    def create_environment_config(self):
        """Create environment-specific configuration"""
        config = self.config[self.environment]

        env_config = {
            "ENVIRONMENT": self.environment,
            "PORT": config["port"],
            "DATABASE_URL": f"sqlite:///data/{config['database']}",
            "MAX_BETA_USERS": config["max_users"],
            "BETA_MODE": str(config["features"]["beta_features"]).lower(),
            "USER_AUTHENTICATION": str(config["features"]["user_authentication"]).lower(),
            "FEEDBACK_COLLECTION": str(config["features"]["feedback_collection"]).lower(),
            "PERFORMANCE_MONITORING": str(config["features"]["performance_monitoring"]).lower(),
            "SECRET_KEY": secrets.token_urlsafe(32),
            "LOG_LEVEL": "DEBUG" if self.environment == "beta" else "INFO"
        }

        # Write .env file
        env_file = Path(f".env.{self.environment}")
        with open(env_file, 'w') as f:
            for key, value in env_config.items():
                f.write(f"{key}={value}\n")

        self.logger.info(f"✅ Environment config created: {env_file}")
        return env_config

    def setup_database(self):
        """Initialize beta database with required tables"""
        config = self.config[self.environment]
        db_path = f"data/{config['database']}"

        self.logger.info(f"Setting up database: {db_path}")

        # Initialize beta user system
        from beta_user_system import BetaUserManager
        user_manager = BetaUserManager(db_path)

        # Initialize monitoring system
        from beta_monitoring_system import BetaMonitoringSystem
        monitoring = BetaMonitoringSystem(db_path)

        self.logger.info("✅ Database initialized with all required tables")

    def create_startup_script(self):
        """Create startup script for the beta environment"""
        config = self.config[self.environment]

        startup_script = f"""#!/bin/bash
# Beta Environment Startup Script
# Generated on {datetime.now()}

export ENVIRONMENT={self.environment}
export PORT={config['port']}

# Load environment variables
if [ -f .env.{self.environment} ]; then
    export $(cat .env.{self.environment} | xargs)
fi

# Start data pipeline in background
echo "Starting data pipeline..."
python data_pipeline.py schedule &
PIPELINE_PID=$!
echo "Data pipeline started with PID: $PIPELINE_PID"

# Start monitoring system
echo "Starting monitoring system..."
python -c "from beta_monitoring_system import start_monitoring; start_monitoring()" &
MONITOR_PID=$!
echo "Monitoring started with PID: $MONITOR_PID"

# Start web application
echo "Starting web application on port {config['port']}..."
streamlit run production_web_app.py --server.port={config['port']} --server.address=0.0.0.0

# Cleanup on exit
trap "kill $PIPELINE_PID $MONITOR_PID" EXIT
"""

        script_path = Path(f"start_{self.environment}.sh")
        with open(script_path, 'w') as f:
            f.write(startup_script)

        # Make executable
        script_path.chmod(0o755)
        self.logger.info(f"✅ Startup script created: {script_path}")

    def create_systemd_service(self):
        """Create systemd service for production deployment"""
        if self.environment != "beta":
            return

        service_content = f"""[Unit]
Description=Vietnam Stock Analysis Beta System
After=network.target

[Service]
Type=simple
User={os.getenv('USER', 'ubuntu')}
WorkingDirectory={self.base_dir}
Environment=ENVIRONMENT=beta
ExecStart={self.base_dir}/start_beta.sh
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
"""

        service_file = Path(f"vietnam-stock-analysis-{self.environment}.service")
        with open(service_file, 'w') as f:
            f.write(service_content)

        self.logger.info(f"✅ Systemd service created: {service_file}")
        self.logger.info("To install: sudo cp vietnam-stock-analysis-beta.service /etc/systemd/system/")
        self.logger.info("Then run: sudo systemctl enable vietnam-stock-analysis-beta")

    def setup_nginx_config(self):
        """Create Nginx configuration for reverse proxy"""
        config = self.config[self.environment]

        nginx_config = f"""# Vietnam Stock Analysis {self.environment.title()} Environment
# Place this in /etc/nginx/sites-available/vietnam-stock-{self.environment}

server {{
    listen 80;
    server_name {self.environment}.vietnam-stocks.com;  # Replace with your domain

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Rate limiting
    limit_req_zone $binary_remote_addr zone={self.environment}:10m rate=10r/m;
    limit_req zone={self.environment} burst=20 nodelay;

    location / {{
        proxy_pass http://127.0.0.1:{config['port']};
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 86400;
    }}

    # Health check endpoint
    location /health {{
        proxy_pass http://127.0.0.1:{config['port']}/health;
        access_log off;
    }}
}}
"""

        nginx_file = Path(f"nginx_{self.environment}.conf")
        with open(nginx_file, 'w') as f:
            f.write(nginx_config)

        self.logger.info(f"✅ Nginx config created: {nginx_file}")

    def create_monitoring_dashboard(self):
        """Create monitoring dashboard script"""
        dashboard_script = f"""#!/usr/bin/env python3
\"\"\"
Beta Monitoring Dashboard
Real-time monitoring for {self.environment} environment
\"\"\"

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from beta_monitoring_system import BetaMonitoringSystem

st.set_page_config(
    page_title="Beta Monitoring Dashboard",
    page_icon="📊",
    layout="wide"
)

# Initialize monitoring
@st.cache_resource
def init_monitoring():
    return BetaMonitoringSystem()

monitoring = init_monitoring()

st.title("🎯 Beta Testing Monitoring Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
days = st.sidebar.selectbox("Time Period", [1, 7, 14, 30], index=1)
auto_refresh = st.sidebar.checkbox("Auto Refresh (30s)", value=True)

if auto_refresh:
    st.rerun()

# Get analytics data
analytics = monitoring.get_user_analytics(days=days)
health = monitoring.get_system_health()

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Active Users Today", health.get('active_users_today', 0))

with col2:
    accuracy = health.get('signal_accuracy_today')
    st.metric("Signal Accuracy Today",
             f"{{accuracy:.1%}}" if accuracy else "No data")

with col3:
    total_signals = analytics.get('signal_performance', {{}}).get('total_signals', 0)
    st.metric("Total Signals", total_signals)

with col4:
    avg_return = analytics.get('signal_performance', {{}}).get('avg_return', 0)
    st.metric("Avg Return", f"{{avg_return:.2%}}" if avg_return else "No data")

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Daily Engagement")
    if analytics.get('daily_engagement'):
        df = pd.DataFrame(analytics['daily_engagement'])
        fig = px.line(df, x='date', y='active_users', title='Active Users Over Time')
        st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Feature Usage")
    if analytics.get('feature_usage'):
        df = pd.DataFrame(analytics['feature_usage'])
        fig = px.bar(df, x='feature_name', y='total_usage', title='Most Used Features')
        st.plotly_chart(fig, use_container_width=True)

# System health
st.subheader("System Health")
if health.get('recent_errors'):
    st.warning("Recent errors detected!")
    error_df = pd.DataFrame(health['recent_errors'])
    st.dataframe(error_df)
else:
    st.success("No errors in the last 24 hours")

# Raw data (expandable)
with st.expander("Raw Analytics Data"):
    st.json(analytics)
"""

        dashboard_file = Path(f"monitoring_dashboard_{self.environment}.py")
        with open(dashboard_file, 'w') as f:
            f.write(dashboard_script)

        dashboard_file.chmod(0o755)
        self.logger.info(f"✅ Monitoring dashboard created: {dashboard_file}")

    def run_health_check(self) -> bool:
        """Run post-deployment health check"""
        self.logger.info("Running deployment health check...")

        checks = [
            ("Database connection", self.check_database_connection),
            ("Signal system", self.check_signal_system),
            ("Data pipeline", self.check_data_pipeline),
            ("Monitoring system", self.check_monitoring_system)
        ]

        all_passed = True
        for check_name, check_func in checks:
            try:
                if check_func():
                    self.logger.info(f"✅ {check_name}: OK")
                else:
                    self.logger.error(f"❌ {check_name}: FAILED")
                    all_passed = False
            except Exception as e:
                self.logger.error(f"❌ {check_name}: ERROR - {e}")
                all_passed = False

        return all_passed

    def check_database_connection(self) -> bool:
        """Check database connectivity"""
        config = self.config[self.environment]
        db_path = f"data/{config['database']}"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        conn.close()

        return result is not None

    def check_signal_system(self) -> bool:
        """Check signal generation system"""
        try:
            from smart_money_signal_system import SmartMoneySignalSystem
            system = SmartMoneySignalSystem()
            # Test with a known stock
            result = system.generate_smart_money_signals('VCB')
            return 'error' not in result
        except Exception:
            return False

    def check_data_pipeline(self) -> bool:
        """Check data pipeline"""
        try:
            from data_pipeline import VietnamStockDataPipeline
            pipeline = VietnamStockDataPipeline()
            return True
        except Exception:
            return False

    def check_monitoring_system(self) -> bool:
        """Check monitoring system"""
        try:
            from beta_monitoring_system import BetaMonitoringSystem
            monitoring = BetaMonitoringSystem()
            return True
        except Exception:
            return False

    def deploy(self):
        """Execute complete deployment"""
        self.logger.info(f"🚀 Starting {self.environment} environment deployment...")

        try:
            # Step 1: Prerequisites
            if not self.check_prerequisites():
                raise Exception("Prerequisites check failed")

            # Step 2: Install dependencies
            self.install_dependencies()

            # Step 3: Create configuration
            self.create_environment_config()

            # Step 4: Setup database
            self.setup_database()

            # Step 5: Create startup scripts
            self.create_startup_script()

            # Step 6: Create systemd service (for production)
            self.create_systemd_service()

            # Step 7: Create Nginx config
            self.setup_nginx_config()

            # Step 8: Create monitoring dashboard
            self.create_monitoring_dashboard()

            # Step 9: Health check
            if not self.run_health_check():
                self.logger.warning("Some health checks failed, but deployment completed")

            self.logger.info("🎉 Deployment completed successfully!")
            self.print_deployment_summary()

        except Exception as e:
            self.logger.error(f"❌ Deployment failed: {e}")
            raise

    def print_deployment_summary(self):
        """Print deployment summary"""
        config = self.config[self.environment]

        summary = f"""
🎯 DEPLOYMENT SUMMARY - {self.environment.upper()} ENVIRONMENT

✅ Environment: {self.environment}
✅ Port: {config['port']}
✅ Database: data/{config['database']}
✅ Max Users: {config['max_users']}

📝 Next Steps:
1. Start the system: ./start_{self.environment}.sh
2. Access web interface: http://localhost:{config['port']}
3. Monitor system: python monitoring_dashboard_{self.environment}.py

🔧 Optional Configuration:
- Configure SSL: Update nginx config with your domain
- Install systemd service: sudo cp vietnam-stock-analysis-{self.environment}.service /etc/systemd/system/
- Set up monitoring alerts: Configure SMTP settings in .env.{self.environment}

📊 Monitoring:
- Logs: logs/
- Health check: http://localhost:{config['port']}/health
- Analytics: Run monitoring dashboard

🎉 Beta environment is ready for testing!
"""

        print(summary)
        self.logger.info("Deployment summary printed")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deploy Vietnam Stock Analysis System")
    parser.add_argument("--environment", choices=["beta", "production"],
                       default="beta", help="Deployment environment")
    parser.add_argument("--skip-health-check", action="store_true",
                       help="Skip post-deployment health check")

    args = parser.parse_args()

    # Create deployer and run deployment
    deployer = BetaEnvironmentDeployer(args.environment)

    try:
        deployer.deploy()
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        sys.exit(1)