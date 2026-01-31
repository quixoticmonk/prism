"""
Terraform Agent - Specialist for Terraform operations
"""

from pathlib import Path
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


@tool
def create_terraform_file(filepath: str, content: str) -> str:
    """Create a Terraform configuration file"""
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return f"Created Terraform file: {filepath}"
    except Exception as e:
        return f"Error creating file {filepath}: {e}"


def create_terraform_agent(bedrock_model):
    """Create Terraform specialist agent"""
    from strands_tools import shell, file_read
    
    terraform_mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="finch",
            args=["run", "-i", "--rm", "hashicorp/terraform-mcp-server"]
        )
    ))
    
    return Agent(
        model=bedrock_model,
        tools=[create_terraform_file, shell, file_read, terraform_mcp_client],
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

CRITICAL: After each test, ALWAYS use shell tool to clean up ONLY these large files (KEEP the directory and .tf files):
- rm -rf issue_<issue_id>/.terraform
- rm -f issue_<issue_id>/.terraform.lock.hcl
- rm -f issue_<issue_id>/terraform.tfstate
- rm -f issue_<issue_id>/terraform.tfstate.backup

IMPORTANT: DO NOT delete the issue_<issue_id> directory itself or any .tf files - these must be preserved for review.

Always work in isolated test directories named issue_<issue_id> for each issue.
Always run terraform destroy after successful apply operations to clean up AWS resources."""
    )
