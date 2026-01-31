#!/bin/bash

# PRISM Agent Runner
# This script sets up and runs the Strands-based PRISM agent

set -e

echo "Starting PRISM - Provider Resource Issue Scanning & Monitoring"

# Install dependencies with uv
echo "Installing dependencies with uv..."
uv sync

# Check if Terraform is installed
if ! command -v terraform &> /dev/null; then
    echo "ERROR: Terraform is not installed. Please install Terraform first."
    echo "   Visit: https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi

# Run the agent
echo "Running AWSCC triage agent..."
uv run python main.py

echo "Triage complete!"
