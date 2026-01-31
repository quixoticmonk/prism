# PRISM - Provider Resource Issue Scanning & Monitoring

**PRISM** is an intelligent Strands-based agent that automatically analyzes and tests AWSCC (AWS Cloud Control) provider issues from the Terraform provider repository. It helps maintainers quickly understand, reproduce, and validate configuration problems.

## What PRISM Does

**Issue Discovery**: Automatically fetches issues labeled `needs-triage` from the terraform-provider-awscc repository

**Configuration Testing**: Extracts Terraform configurations from issue descriptions and tests them in isolated environments

**Automated Analysis**: Runs `terraform init`, `plan`, and `apply` to reproduce reported problems

**Documentation**: Generates comprehensive markdown reports with test results, error analysis, and reproduction steps

**Clean Environment**: Automatically cleans up test directories and lock files after each analysis

## Key Features

- **Multi-Agent Architecture**: Uses specialized sub-agents for different aspects of issue analysis
- **GitHub Integration**: Seamlessly connects to GitHub API to fetch and analyze issues
- **Terraform Automation**: Full Terraform lifecycle testing with proper error handling
- **Intelligent Filtering**: Excludes resource-suppression issues and focuses on recent problems
- **Structured Output**: Creates organized documentation for each analyzed issue

## Quick Start

1. **Setup Environment**:
   ```bash
   ./run_triage.sh
   ```

2. **Configure Settings** (optional):
   Edit `agent_config.json` to customize:
   - Maximum age of issues to analyze
   - Number of issues to process
   - Output file locations

3. **Run Analysis**:
   The agent will automatically:
   - Fetch qualifying issues
   - Extract configurations
   - Test each configuration
   - Generate analysis reports

## Configuration

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
    "max_issues": 1
  },
  "output": {
    "results_file": "triage_results.md",
    "issues_dir": "triage_issues"
  }
}
```

## Output

PRISM generates:
- **`triage_results.md`**: Comprehensive analysis report
- **`triage_issues/`**: Individual test directories for each issue
- **Detailed logs**: Step-by-step execution information

## Requirements

- Python 3.8+
- Terraform CLI
- AWS CLI configured
- GitHub access (for API calls)
- Strands SDK

## Architecture

PRISM uses a multi-agent approach:
- **Orchestrator Agent**: Coordinates the overall workflow
- **GitHub Agent**: Handles issue fetching and parsing
- **Terraform Agent**: Manages configuration testing
- **Documentation Agent**: Generates analysis reports

Built with the Strands SDK for robust agent orchestration and AWS Bedrock for intelligent analysis.
