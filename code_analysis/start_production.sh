#!/bin/bash
# Beta Environment Startup Script
# Generated on 2025-09-16 03:08:09.710110

export ENVIRONMENT=production
export PORT=8501

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | xargs)
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
echo "Starting web application on port 8501..."
streamlit run production_web_app.py --server.port=8501 --server.address=0.0.0.0

# Cleanup on exit
trap "kill $PIPELINE_PID $MONITOR_PID" EXIT
