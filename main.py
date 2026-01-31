#!/usr/bin/env python3
"""
PRISM - Provider Resource Issue Scanning & Monitoring

Main entry point for the multi-agent system.
"""

import os
import signal
import sys

# Configure automated tool execution - bypass consent prompts for shell commands
os.environ["BYPASS_TOOL_CONSENT"] = "true"

from agents import PRISMOrchestrator


def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\nShutting down gracefully...")
    sys.exit(0)


def main():
    """Main entry point"""
    print("Multi-Agent PRISM System")
    print("=" * 50)
    
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        with PRISMOrchestrator() as orchestrator:
            response = orchestrator.run_triage()
            print(response)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Force cleanup any remaining resources
        import gc
        gc.collect()


if __name__ == "__main__":
    main()
