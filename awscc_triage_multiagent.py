#!/usr/bin/env python3
"""
PRISM - Provider Resource Issue Scanning & Monitoring

Multi-agent system for analyzing AWSCC provider issues.
"""

import os
import requests
from pathlib import Path

# Configure automated tool execution - bypass consent prompts for shell commands
os.environ["BYPASS_TOOL_CONSENT"] = "true"
from strands import Agent, tool
from strands.models import BedrockModel
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters

class PRISMOrchestrator:
    def __init__(self):
        # Load configuration
        config_path = Path("agent_config.json")
        if config_path.exists():
            import json
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
        
        # Configure GitHub MCP client
        self.github_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="npx",
                args=["-y", "@modelcontextprotocol/server-github"]
            )
        ))
        
        # Configure AWS Documentation MCP client
        self.aws_docs_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="uvx",
                args=["awslabs.aws-documentation-mcp-server@latest"]
            )
        ))
        self.terraform_mcp_client = MCPClient(lambda: stdio_client(
            StdioServerParameters(
                command="finch",
                args=["run", "-i", "--rm", "hashicorp/terraform-mcp-server"]
            )
        ))
        
        # Initialize specialized agents
        self.github_agent = self._create_github_agent()
        self.terraform_agent = self._create_terraform_agent()
        self.analysis_agent = self._create_analysis_agent()
        
        # Create orchestrator agent with tools to manage sub-agents
        self.orchestrator = self._create_orchestrator()
    
    def _create_github_agent(self):
        """Create GitHub specialist agent"""
        return Agent(
            model=self.bedrock_model,
            tools=[self.github_mcp_client],
            system_prompt="""You are a GitHub specialist. Your job is to find and analyze GitHub issues from the terraform-provider-awscc repository.

Use the GitHub MCP tools to:
1. Search for issues in the hashicorp/terraform-provider-awscc repository
2. Filter for issues with 'needs-triage' label
3. Exclude issues with 'resource-suppression' label  
4. Focus on issues created within the last 10 days
5. Extract issue numbers, titles, descriptions, and any Terraform configurations from issue bodies

When searching, use parameters like:
- repository: "hashicorp/terraform-provider-awscc"
- labels: ["needs-triage"]
- state: "open"
- sort: "created"
- direction: "desc"

Extract and analyze the Terraform configurations found in issue descriptions for testing."""
        )
    
    def _create_terraform_agent(self):
        """Create Terraform specialist agent"""
        from strands_tools import shell, file_read
        
        return Agent(
            model=self.bedrock_model,
            tools=[self._create_terraform_file, shell, file_read, self.terraform_mcp_client],
            system_prompt="""You are a Terraform specialist. Your job is to:
1. Create Terraform test environments with proper configurations using LATEST provider versions
2. Use Terraform MCP tools to get the latest AWSCC provider version before creating configurations
3. Use shell tool to run terraform commands (init, validate, plan, apply, destroy)
4. Use file_read to examine existing terraform files and configurations
5. Analyze terraform outputs and errors
6. Clean up test environments and AWS resources
7. ALWAYS clean up large Terraform files after testing using shell tool

IMPORTANT: Always use the latest AWSCC provider version in configurations:
- Use Terraform MCP tools to query the latest version of hashicorp/awscc provider
- Include the latest version in terraform configuration blocks

Use shell tool for terraform operations:
- Create test directory: mkdir -p issue_<issue_id>
- cd issue_<issue_id>
- terraform init
- terraform validate  
- terraform plan
- terraform apply -auto-approve
- terraform destroy -auto-approve

CRITICAL: After each test, ALWAYS use shell tool to clean up large files:
- rm -rf issue_<issue_id>/.terraform
- rm -f issue_<issue_id>/.terraform.lock.hcl
- rm -f issue_<issue_id>/terraform.tfstate
- rm -f issue_<issue_id>/terraform.tfstate.backup

Always work in isolated test directories named issue_<issue_id> for each issue.
Always run terraform destroy after successful apply operations to clean up AWS resources."""
        )
    
    def _create_analysis_agent(self):
        """Create Analysis specialist agent"""
        from strands_tools import file_read, file_write
        
        return Agent(
            model=self.bedrock_model,
            tools=[self._analyze_terraform_output, self._write_triage_report, self.aws_docs_mcp_client, file_read, file_write],
            system_prompt="""You are an AWS and Terraform expert analyst. Your job is to:
1. Analyze terraform command outputs and errors
2. Provide expert insights on CloudFormation schema issues
3. Create comprehensive triage reports with recommendations
4. Identify root causes and suggest solutions
5. Use AWS documentation MCP tools to get latest AWS service information
6. Use file_read to examine terraform files and outputs
7. Use file_write to create detailed analysis reports

Focus on AWSCC provider issues and CloudFormation schema discrepancies."""
        )
    
    @tool
    def _create_terraform_file(self, filepath: str, content: str) -> str:
        """Create a Terraform configuration file"""
        try:
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            with open(filepath, 'w') as f:
                f.write(content)
            return f"Created Terraform file: {filepath}"
        except Exception as e:
            return f"Error creating file {filepath}: {e}"
    
    @tool
    def _analyze_terraform_output(self, command: str, output: str, issue_context: str) -> str:
        """Analyze terraform command output and provide expert insights"""
        return f"Analyzing terraform {command} output:\n{output}\n\nIssue context: {issue_context}"
    
    @tool
    def _write_triage_report(self, issue_id: str, content: str) -> str:
        """Write a comprehensive triage report for an issue"""
        filename = f"triage_issue_{issue_id}.md"
        filepath = Path.cwd() / filename
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Report written to: {filepath}"
    
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
3. Delegate to Analysis Agent to analyze results and create reports
4. Ensure proper cleanup of AWS resources

Use your delegation tools to coordinate the specialized agents and ensure comprehensive triage."""
        )
    
    def run_triage(self):
        """Run the complete triage process"""
        try:
            # Load configuration
            config_path = Path("agent_config.json")
            if config_path.exists():
                import json
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
2. For each issue found, delegate to Terraform Agent to:
   - First get the latest AWSCC provider version using Terraform MCP tools
   - Create test configurations using the latest provider version
   - Test the configurations with terraform commands
   - ALWAYS clean up large terraform files after testing
3. Delegate to Analysis Agent to create detailed reports
4. Ensure all AWS resources are properly cleaned up

Start the triage process by delegating to the GitHub Agent with the above configuration."""
            
            return self.orchestrator(prompt)
        finally:
            # Cleanup MCP clients
            self._cleanup_mcp_clients()
    
    def _cleanup_mcp_clients(self):
        """Properly cleanup MCP clients to avoid shutdown errors"""
        try:
            if hasattr(self, 'github_mcp_client'):
                self.github_mcp_client.__exit__(None, None, None)
            if hasattr(self, 'aws_docs_mcp_client'):
                self.aws_docs_mcp_client.__exit__(None, None, None)
            if hasattr(self, 'terraform_mcp_client'):
                self.terraform_mcp_client.__exit__(None, None, None)
        except Exception:
            pass  # Ignore cleanup errors during shutdown

def main():
    """Main entry point"""
    print("Multi-Agent PRISM System")
    print("=" * 50)
    
    try:
        orchestrator = PRISMOrchestrator()
        response = orchestrator.run_triage()
        print(response)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(sig, frame):
        print("\n🛑 Shutting down gracefully...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    main()
