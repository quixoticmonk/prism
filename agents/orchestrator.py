"""
PRISM Orchestrator - Main coordination agent
"""

import os
import json
import subprocess
from pathlib import Path
from strands import Agent, tool
from strands.models import BedrockModel
from .github_agent import create_github_agent
from .terraform_agent import create_terraform_agent
from .analysis_agent import create_analysis_agent


class PRISMOrchestrator:
    def __init__(self):
        # Load configuration
        config_path = Path("agent_config.json")
        if config_path.exists():
            with open(config_path) as f:
                config = json.load(f)
        else:
            config = {}
        
        # Configure Bedrock model from config
        model_config = config.get("model", {})
        self.bedrock_model = BedrockModel(
            model_id=model_config.get("model_id", "us.anthropic.claude-sonnet-4-20250514-v1:0"),
            temperature=model_config.get("temperature", 0.3),
            max_tokens=model_config.get("max_tokens", 4096)
        )
        
        # Initialize specialized agents
        self.github_agent = create_github_agent(self.bedrock_model)
        self.terraform_agent = create_terraform_agent(self.bedrock_model)
        self.analysis_agent = create_analysis_agent(self.bedrock_model)
        
        # Create orchestrator agent with tools to manage sub-agents
        self.orchestrator = self._create_orchestrator()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
    
    def cleanup(self):
        """Clean up agents and resources"""
        try:
            if hasattr(self, 'github_agent'):
                del self.github_agent
            if hasattr(self, 'terraform_agent'):
                del self.terraform_agent
            if hasattr(self, 'analysis_agent'):
                del self.analysis_agent
            if hasattr(self, 'orchestrator'):
                del self.orchestrator
        except Exception:
            pass  # Ignore cleanup errors
    
    @tool
    def delegate_to_github_agent(self, task: str) -> str:
        """Delegate a task to the GitHub specialist agent"""
        return self.github_agent(task)
    
    @tool
    def delegate_to_terraform_agent(self, task: str) -> str:
        """Delegate a task to the Terraform specialist agent"""
        return self.terraform_agent(task)
    
    @tool
    def delegate_to_analysis_agent(self, task: str) -> str:
        """Delegate a task to the Analysis specialist agent"""
        return self.analysis_agent(task)
    
    def _create_orchestrator(self):
        """Create the main orchestrator agent"""
        return Agent(
            model=self.bedrock_model,
            tools=[
                self.delegate_to_github_agent,
                self.delegate_to_terraform_agent, 
                self.delegate_to_analysis_agent
            ],
            system_prompt="""You are the orchestrator for AWSCC provider issue triage. 

You manage three specialized agents:
- GitHub Agent: Fetches issues and extracts configurations
- Terraform Agent: Creates environments and runs terraform workflows  
- Analysis Agent: Analyzes results and creates reports

Your workflow:
1. Delegate to GitHub Agent to fetch recent issues
2. For each issue, delegate to Terraform Agent to test configurations
3. MANDATORY: After each terraform test, call self.cleanup_terraform_files(issue_id)
4. Delegate to Analysis Agent to analyze results and create reports
5. Ensure proper cleanup of AWS resources

Use your delegation tools to coordinate the specialized agents and ensure comprehensive triage."""
        )
    
    def run_triage(self):
        """Run the complete triage process"""
        try:
            # Load configuration
            config_path = Path("agent_config.json")
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                max_issues = config.get("github", {}).get("max_issues", 1)
                max_age_days = config.get("github", {}).get("max_age_days", 10)
            else:
                max_issues = 1
                max_age_days = 10
                
            prompt = f"""Please coordinate a comprehensive AWSCC provider issue triage:

CONFIGURATION:
- Maximum issues to process: {max_issues}
- Maximum age of issues: {max_age_days} days
- Repository: hashicorp/terraform-provider-awscc
- Include labels: needs-triage
- Exclude labels: resource-suppression

CRITICAL REQUIREMENT:
- ALL Terraform configurations MUST use the LATEST AWSCC provider version
- Terraform Agent must query the latest provider version using Terraform MCP tools before creating any configurations

WORKFLOW:
1. Delegate to GitHub Agent to fetch recent issues (limit to {max_issues} issues)
2. For each issue found:
   a. Delegate to Terraform Agent to:
      - First get the latest AWSCC provider version using Terraform MCP tools
      - Create test configurations using the latest provider version
      - Test the configurations with terraform commands
   b. MANDATORY: Call cleanup_terraform_files(issue_id) immediately after terraform testing
   c. Delegate to Analysis Agent to analyze results and create reports
      - Generate ONE comprehensive report per issue as triage_issue_<id>.md
      - Avoid creating multiple reports for the same issue
3. Delegate to Analysis Agent to create detailed reports
4. Ensure all AWS resources are properly cleaned up

Start the triage process by delegating to the GitHub Agent with the above configuration."""
            
            # Execute with cleanup protection
            try:
                result = self.orchestrator(prompt)
                return result
            finally:
                # Always attempt cleanup of any terraform files that might remain
                for item in os.listdir('.'):
                    if item.startswith('issue_') and os.path.isdir(item):
                        issue_id = item.replace('issue_', '')
                        self.cleanup_terraform_files(issue_id)
                        print(f"Final cleanup performed for {item} (kept .tf files)")
        except Exception as e:
            print(f"Error during triage: {e}")
            return str(e)
        finally:
            # Cleanup resources
            self.cleanup()
    
    def cleanup_terraform_files(self, issue_id):
        """Clean up large terraform files after testing, keep .tf files for review"""
        issue_dir = f"issue_{issue_id}"
        if os.path.exists(issue_dir):
            cleanup_commands = [
                f"rm -rf {issue_dir}/.terraform",
                f"rm -f {issue_dir}/.terraform.lock.hcl",
                f"rm -f {issue_dir}/terraform.tfstate",
                f"rm -f {issue_dir}/terraform.tfstate.backup"
            ]
            
            for cmd in cleanup_commands:
                try:
                    subprocess.run(cmd.split(), check=False)
                    print(f"Cleaned up: {cmd}")
                except Exception as e:
                    print(f"Cleanup warning: {e}")
            
            # Keep .tf files and directory for review
            print(f"Preserved .tf files in {issue_dir}/ for review")
