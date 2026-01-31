"""
GitHub Agent - Specialist for GitHub issue analysis
"""

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


def create_github_agent(bedrock_model):
    """Create GitHub specialist agent"""
    github_mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="npx", args=["-y", "@modelcontextprotocol/server-github"]
            )
        )
    )

    return Agent(
        model=bedrock_model,
        tools=[github_mcp_client],
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

Extract and analyze the Terraform configurations found in issue descriptions for testing.""",
    )
