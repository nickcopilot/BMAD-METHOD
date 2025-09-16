#!/bin/bash
# Vietnam Stock Analysis System - Production Deployment Script

set -e  # Exit on any error

echo "🇻🇳 Vietnam Stock Analysis System - Production Deployment"
echo "=========================================================="

# Configuration
APP_NAME="vietnam-stock-analysis"
PORT=${PORT:-8501}
ENVIRONMENT=${ENVIRONMENT:-production}
DOMAIN=${DOMAIN:-localhost}

echo "📋 Deployment Configuration:"
echo "   App Name: $APP_NAME"
echo "   Port: $PORT"
echo "   Environment: $ENVIRONMENT"
echo "   Domain: $DOMAIN"
echo ""

# Step 1: Environment Setup
echo "🔧 Step 1: Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip

# Step 2: Install Dependencies
echo "📦 Step 2: Installing production dependencies..."
pip install -r requirements_production.txt

# Step 3: Environment Variables
echo "⚙️ Step 3: Setting up environment variables..."
cat > .env << EOF
# Vietnam Stock Analysis System - Production Configuration
ENVIRONMENT=production
PORT=$PORT
DOMAIN=$DOMAIN

# Application Settings
APP_NAME=$APP_NAME
DEBUG=False
LOG_LEVEL=INFO

# Database Configuration (future use)
DATABASE_URL=sqlite:///vietnam_stocks.db

# Redis Configuration (caching)
REDIS_URL=redis://localhost:6379/0

# Email Configuration (for alerts)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS Configuration (future use)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number

# Vietnamese Stock Data API
VNSTOCK_API_KEY=your-vnstock-key

# Security
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000

# Performance
STREAMLIT_CACHE_TTL=300
MAX_CONCURRENT_ANALYSES=10
EOF

echo "✅ Environment file created: .env"

# Step 4: Create Systemd Service (Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "🔧 Step 4: Creating systemd service..."

    sudo tee /etc/systemd/system/$APP_NAME.service > /dev/null << EOF
[Unit]
Description=Vietnam Stock Analysis System
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$(pwd)
Environment=PATH=$(pwd)/venv/bin
ExecStart=$(pwd)/venv/bin/streamlit run production_web_app.py --server.port=$PORT --server.address=0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable $APP_NAME
    echo "✅ Systemd service created and enabled"
fi

# Step 5: Nginx Configuration (if nginx is available)
if command -v nginx &> /dev/null; then
    echo "🌐 Step 5: Configuring Nginx reverse proxy..."

    sudo tee /etc/nginx/sites-available/$APP_NAME > /dev/null << EOF
server {
    listen 80;
    server_name $DOMAIN;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1000;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        proxy_pass http://localhost:$PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # Streamlit specific
        proxy_buffering off;
        proxy_read_timeout 86400;
    }

    # Static files (future use)
    location /static/ {
        alias $(pwd)/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Health check endpoint
    location /health {
        proxy_pass http://localhost:$PORT/_stcore/health;
    }
}
EOF

    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    echo "✅ Nginx configuration created and reloaded"
else
    echo "⚠️ Nginx not found, skipping reverse proxy setup"
fi

# Step 6: Create startup script
echo "🚀 Step 6: Creating startup script..."
cat > start_production.sh << 'EOF'
#!/bin/bash
# Vietnam Stock Analysis System - Production Startup

source venv/bin/activate
source .env

echo "🇻🇳 Starting Vietnam Stock Analysis System..."
echo "Environment: $ENVIRONMENT"
echo "Port: $PORT"
echo "Time: $(date)"

# Start the application
streamlit run production_web_app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=true \
    --server.maxUploadSize=50 \
    --browser.gatherUsageStats=false
EOF

chmod +x start_production.sh

# Step 7: Create monitoring script
echo "📊 Step 7: Creating monitoring script..."
cat > monitor.sh << 'EOF'
#!/bin/bash
# Vietnam Stock Analysis System - Health Monitoring

APP_NAME="vietnam-stock-analysis"
PORT=${PORT:-8501}
LOG_FILE="logs/monitor.log"

# Create logs directory
mkdir -p logs

check_service_health() {
    echo "$(date): Checking service health..." >> $LOG_FILE

    # Check if service is running
    if systemctl is-active --quiet $APP_NAME; then
        echo "$(date): ✅ Service is running" >> $LOG_FILE
    else
        echo "$(date): ❌ Service is not running, attempting restart..." >> $LOG_FILE
        sudo systemctl restart $APP_NAME
        sleep 10
    fi

    # Check HTTP response
    if curl -f -s http://localhost:$PORT/_stcore/health > /dev/null; then
        echo "$(date): ✅ HTTP health check passed" >> $LOG_FILE
    else
        echo "$(date): ❌ HTTP health check failed" >> $LOG_FILE
    fi
}

# Run health check
check_service_health

# Show recent logs
echo "Recent logs:"
tail -n 10 $LOG_FILE
EOF

chmod +x monitor.sh

# Step 8: Setup log rotation
echo "📝 Step 8: Setting up log rotation..."
sudo tee /etc/logrotate.d/$APP_NAME > /dev/null << EOF
$(pwd)/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 $USER $USER
}
EOF

# Step 9: Create production configuration
echo "⚙️ Step 9: Creating Streamlit production config..."
mkdir -p ~/.streamlit
cat > ~/.streamlit/config.toml << EOF
[server]
port = $PORT
address = "0.0.0.0"
headless = true
enableCORS = false
enableXsrfProtection = true
maxUploadSize = 50

[browser]
gatherUsageStats = false

[theme]
primaryColor = "#1e3d59"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[logger]
level = "info"
messageFormat = "%(asctime)s %(message)s"
EOF

# Step 10: Set up cron job for monitoring
echo "⏰ Step 10: Setting up monitoring cron job..."
(crontab -l 2>/dev/null; echo "*/5 * * * * $(pwd)/monitor.sh") | crontab -

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================="
echo ""
echo "📋 Next Steps:"
echo "1. Update .env file with your actual credentials"
echo "2. Start the service: sudo systemctl start $APP_NAME"
echo "3. Check status: sudo systemctl status $APP_NAME"
echo "4. View logs: sudo journalctl -u $APP_NAME -f"
echo "5. Access application: http://$DOMAIN"
echo ""
echo "🔧 Management Commands:"
echo "  Start:   sudo systemctl start $APP_NAME"
echo "  Stop:    sudo systemctl stop $APP_NAME"
echo "  Restart: sudo systemctl restart $APP_NAME"
echo "  Status:  sudo systemctl status $APP_NAME"
echo "  Logs:    sudo journalctl -u $APP_NAME -f"
echo ""
echo "📊 Monitoring:"
echo "  Health:  ./monitor.sh"
echo "  Logs:    tail -f logs/monitor.log"
echo ""
echo "✅ Vietnam Stock Analysis System is ready for production!"