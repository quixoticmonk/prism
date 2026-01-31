"""
Analysis Agent - Specialist for AWS and Terraform analysis
"""

from pathlib import Path
from strands import Agent, tool
from strands.tools.mcp import MCPClient
from mcp import stdio_client, StdioServerParameters


@tool
def analyze_terraform_output(command: str, output: str, issue_context: str) -> str:
    """Analyze terraform command output and provide expert insights"""
    return f"Analyzing terraform {command} output:\n{output}\n\nIssue context: {issue_context}"


@tool
def write_triage_report(issue_id: str, content: str) -> str:
    """Write a comprehensive triage report for an issue"""
    filename = f"triage_issue_{issue_id}.md"
    filepath = Path.cwd() / filename
    with open(filepath, 'w') as f:
        f.write(content)
    return f"Report written to: {filepath}"


def create_analysis_agent(bedrock_model):
    """Create Analysis specialist agent"""
    from strands_tools import file_read, file_write
    
    aws_docs_mcp_client = MCPClient(lambda: stdio_client(
        StdioServerParameters(
            command="uvx",
            args=["awslabs.aws-documentation-mcp-server@latest"]
        )
    ))
    
    return Agent(
        model=bedrock_model,
        tools=[analyze_terraform_output, write_triage_report, aws_docs_mcp_client, file_read, file_write],
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
