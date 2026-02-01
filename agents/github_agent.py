"""
GitHub Agent - Specialist for GitHub issue analysis
"""

from strands import Agent
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


def create_github_agent(bedrock_model):
    """Create GitHub specialist agent"""
    import os
    github_mcp_client = MCPClient(
        lambda: stdio_client(
            StdioServerParameters(
                command="finch", 
                args=[
                    "run", "-i", "--rm", 
                    "-e", "GITHUB_PERSONAL_ACCESS_TOKEN",
                    "ghcr.io/github/github-mcp-server"
                ],
                env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv("GITHUB_PERSONAL_ACCESS_TOKEN", "")}
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
6. Add comments to issues with analysis results when requested

When searching, use parameters like:
- repository: "hashicorp/terraform-provider-awscc"
- labels: ["needs-triage"]
- state: "open"
- sort: "created"
- direction: "desc"

For adding comments, use the add_issue_comment tool with:
- owner: "hashicorp"
- repo: "terraform-provider-awscc"
- issue_number: <issue_number>
- body: <comment_content>

Extract and analyze the Terraform configurations found in issue descriptions for testing.""",
    )
