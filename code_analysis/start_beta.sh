#!/bin/bash
# Beta Environment Startup Script
# Generated on 2025-09-16 02:50:51.650423

export ENVIRONMENT=beta
export PORT=8502

# Load environment variables
if [ -f .env.beta ]; then
    export $(cat .env.beta | xargs)
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
echo "Starting web application on port 8502..."
streamlit run production_web_app.py --server.port=8502 --server.address=0.0.0.0

# Cleanup on exit
trap "kill $PIPELINE_PID $MONITOR_PID" EXIT
