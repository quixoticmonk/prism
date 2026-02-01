# 🔍 PRISM - Provider Resource Issue Scanning & Monitoring

**PRISM** is an intelligent multi-agent system built with Strands SDK that automatically analyzes and tests AWSCC (AWS Cloud Control) provider issues from the Terraform provider repository. It helps maintainers quickly understand, reproduce, and validate configuration problems using the latest provider versions.

## 🎯 What PRISM Does

- 🔎 **Issue Discovery**: Automatically fetches issues labeled `needs-triage` from the terraform-provider-awscc repository
- 🚀 **Latest Provider Testing**: Always uses the latest AWSCC provider version for accurate testing
- ⚙️ **Configuration Testing**: Extracts Terraform configurations from issue descriptions and tests them in isolated environments
- 🤖 **Automated Analysis**: Runs complete Terraform lifecycle (`init`, `validate`, `plan`, `apply`, `destroy`) to reproduce reported problems
- 🧹 **Smart Cleanup**: Automatically removes large Terraform files (.terraform/, state files) to save disk space while preserving .tf files and directories for review
- 🏗️ **Modular Architecture**: Clean separation of concerns with specialized agent modules in dedicated directory structure
- 📋 **Documentation**: Generates comprehensive markdown reports with test results, error analysis, and reproduction steps

## ✨ Key Features

- 🏗️ **Multi-Agent Architecture**: Uses specialized MCP-enabled agents for different aspects of issue analysis
- 📦 **Latest Provider Versions**: Automatically queries and uses the latest AWSCC provider version
- 🔗 **GitHub Integration**: Uses GitHub MCP server to fetch and analyze issues
- 🔧 **Terraform Automation**: Full Terraform lifecycle testing with proper error handling and cleanup
- 📚 **AWS Documentation**: Integrates AWS documentation MCP server for expert analysis
- ⚡ **Automated Execution**: Runs without manual confirmation prompts for streamlined operation
- 🎯 **Intelligent Filtering**: Excludes resource-suppression issues and focuses on recent problems
- 🗂️ **Clean Environment**: Automatically cleans up large files and AWS resources after testing

## 🚀 Quick Start

1. **Install Dependencies**:
   ```bash
   uv sync
   ```

2. **Configure Settings** (optional):
   Edit `agent_config.json` to customize:
   - 📅 Maximum age of issues to analyze
   - 🔢 Number of issues to process
   - 🧠 Model configuration

3. **Run Analysis**:
   ```bash
   ./run_triage.sh
   ```
   
   The system will automatically:
   - 📥 Fetch qualifying issues using GitHub MCP
   - 🔄 Get latest AWSCC provider version using Terraform MCP
   - 🧪 Extract and test configurations
   - 🧹 Clean up large files and AWS resources while preserving .tf files
   - 📊 Generate comprehensive analysis reports

## ⚙️ Configuration

The agent behavior is controlled by `agent_config.json`:

```json
{
  "agent": {
    "name": "PRISM",
    "description": "Provider Resource Issue Scanning & Monitoring"
  },
  "github": {
    "repo": "hashicorp/terraform-provider-awscc",
    "labels": {
      "include": ["needs-triage"],
      "exclude": ["resource-suppression"]
    },
    "max_age_days": 10,
    "max_issues": 2
  },
  "model": {
    "model_id": "us.anthropic.claude-sonnet-4-20250514-v1:0",
    "temperature": 0.3,
    "max_tokens": 4096
  }
}
```

## 📤 Output

PRISM generates:
- 📁 **Individual test directories**: `issue_<id>/` for each analyzed issue with preserved .tf files
- 📋 **Triage reports**: `triage_issue_<id>.md` with detailed analysis
- 🧹 **Clean workspace**: Large Terraform files (.terraform/, state files) automatically removed after testing while preserving .tf files for review

## 📋 Requirements

- 🐍 Python 3.12+ with [uv](https://docs.astral.sh/uv/) package manager
- 🏗️ Terraform CLI
- ☁️ AWS CLI configured
- 🔗 GitHub access (for MCP server)
- 🧬 Strands SDK with strands-agents-tools
- 🐳 Docker/Finch (for Terraform MCP server)

## 🏗️ Architecture

PRISM uses a multi-agent MCP-enabled approach with a clean modular structure:

### Project Structure
```
prism/
├── main.py                    # Main entry point
├── agents/                    # Agent modules directory
│   ├── __init__.py           # Package initialization
│   ├── orchestrator.py       # Main coordination agent
│   ├── github_agent.py       # GitHub specialist agent
│   ├── terraform_agent.py    # Terraform specialist agent
│   └── analysis_agent.py     # Analysis specialist agent
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Dependency lock file
├── .python-version          # Python version specification
├── run_triage.sh            # Execution script
└── .gitignore               # Git ignore patterns
```

### Agent Responsibilities
- 🎯 **Orchestrator Agent**: Coordinates the overall workflow and delegates tasks with proper resource cleanup
- 🔗 **GitHub Agent**: Uses GitHub MCP server to fetch and analyze issues
- 🔧 **Terraform Agent**: Uses Terraform MCP server and shell tools for testing with latest provider versions, preserves .tf files while cleaning up large state files
- 📊 **Analysis Agent**: Uses AWS Documentation MCP server for expert analysis and report generation

Built with the Strands SDK for robust agent orchestration, MCP servers for external integrations, and AWS Bedrock for intelligent analysis.

## 📝 TODO

- 🔄 **GitHub Issue Updates**: Update GitHub issues with analysis results once complete. Functionality works but GitHub's fine-grained tokens have limitations compared to classic tokens - despite trying `issues: write` and repo-specific permissions, fine-grained tokens consistently return 403 errors
- 📦 **S3 Storage**: Copy configuration files and analysis results to S3 bucket for deeper analysis (conditional step, nice-to-have since agents already create `issue_id` directories)
- ☁️ **AWS AgentCore Migration**: Convert implementation to AWS AgentCore service
- ⏰ **Scheduled Execution**: Set up weekly automated runs (implementation already filters by `needs-triage` and date limits)
- 📊 **Issue Tracking**: Track already-processed issues using either:
  - Storage-based tracking: Use existing issue IDs to skip duplicates
  - Label-based tracking: Update `needs-triage` label once analysis is posted (preferred if issue metadata updates work)
