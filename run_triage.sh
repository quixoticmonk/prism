#!/bin/bash

# PRISM Agent Runner
# This script sets up and runs the Strands-based PRISM agent

set -e

echo "Starting PRISM - Provider Resource Issue Scanning & Monitoring"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "ERROR: Terraform is not installed. Please install Terraform first."
    echo "   Visit: https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

# Run the agent
echo "Running AWSCC triage agent..."
python awscc_triage_multiagent.py

echo "Triage complete!"
