# Using the Agent Reliability Testing Tool with PromptQL

The Agent Reliability Testing Tool helps evaluate and improve the reliability of your PromptQL-powered applications by measuring two key dimensions:

1. **Visibility**: How well PromptQL explains its reasoning, data sources, and query plans
2. **Repeatability**: How consistently PromptQL responds to the same query across multiple executions

## Prerequisites

- Python 3.8 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- A PromptQL API key 
- Your DDN project SQL endpoint URL
- OpenAI or Anthropic API key (for the evaluation component)

## Setup Instructions

### 1. Clone the Reliability Testing Tool

```bash
git clone https://github.com/hasura/agent-reliability-tool.git
cd agent-reliability-tool
```

### 2. Install Dependencies

```bash
poetry install
```

### 3. Create PromptQL Agent Implementation Files

#### Create the PromptQL Agent Implementation

Create a new file `agent_reliability/promptql_agent.py`:

```bash
# Create the file
nano agent_reliability/promptql_agent.py
```

Add the following code to the file:

```python
"""
PromptQL agent implementation for the reliability testing tool.
"""
import os
import json
import requests
from typing import Dict, Any, Optional

class PromptQLAgent:
    """
    Agent implementation for PromptQL API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the PromptQL agent with configuration.
        
        Args:
            config: Configuration dictionary containing API details
        """
        self.api_url = config.get("api_url", "https://api.promptql.pro.hasura.io/query")
        self.api_key = config.get("api_key", os.environ.get("PROMPTQL_API_KEY"))
        self.ddn_url = config.get("ddn_url", "")
        self.timezone = config.get("timezone", "UTC")
        self.llm_provider = config.get("llm_provider", "hasura")
        
        if not self.api_key:
            raise ValueError("PromptQL API key is required. Set it in config or PROMPTQL_API_KEY environment variable.")
            
        if not self.ddn_url:
            raise ValueError("DDN URL is required for PromptQL. Set it in the config.")
    
    def execute_query(self, query: str) -> str:
        """
        Execute a query on the PromptQL API and return the response as a string.
        
        Args:
            query: The natural language query to send to PromptQL
            
        Returns:
            A string containing the PromptQL response
        """
        # Prepare the request payload
        payload = {
            "version": "v1",
            "llm": {
                "provider": self.llm_provider,
            },
            "ddn": {
                "url": self.ddn_url,
                "headers": {}
            },
            "artifacts": [],
            "timezone": self.timezone,
            "interactions": [
                {
                    "user_message": {
                        "text": query
                    },
                    "assistant_actions": []
                }
            ],
            "stream": False
        }
        
        # Make the API request
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                },
                json=payload
            )
            
            # Check for errors
            if response.status_code != 200:
                return f"Error: PromptQL API returned status code {response.status_code}: {response.text}"
            
            # Parse the response
            result = response.json()
            
            # Format the response components
            formatted_response = ""
            
            if "assistant_actions" in result and result["assistant_actions"]:
                action = result["assistant_actions"][0]  # Get the first action
                
                if "message" in action and action["message"]:
                    formatted_response += f"MESSAGE:\n{action['message']}\n\n"
                    
                if "plan" in action and action["plan"]:
                    formatted_response += f"PLAN:\n{action['plan']}\n\n"
                    
                if "code" in action and action["code"]:
                    formatted_response += f"CODE:\n{action['code']}\n\n"
                    
                if "code_output" in action and action["code_output"]:
                    formatted_response += f"CODE OUTPUT:\n{action['code_output']}\n\n"
                    
                if "code_error" in action and action["code_error"]:
                    formatted_response += f"CODE ERROR:\n{action['code_error']}\n\n"
            
            # Include any artifacts
            if "modified_artifacts" in result and result["modified_artifacts"]:
                formatted_response += "ARTIFACTS:\n"
                for artifact in result["modified_artifacts"]:
                    formatted_response += f"--- {artifact.get('title', 'Untitled')} ({artifact.get('identifier', 'unknown')}) ---\n"
                    formatted_response += f"{artifact.get('data', '')}\n\n"
            
            return formatted_response.strip() or "No response received from PromptQL"
            
        except Exception as e:
            return f"Error connecting to PromptQL: {str(e)}"
```

#### Update the Agent Wrapper

Edit the existing `agent_reliability/agent_wrapper.py` file:

```bash
nano agent_reliability/agent_wrapper.py
```

Replace the contents with:

```python
"""
Agent wrapper for the reliability testing tool.
"""
from typing import Dict, Any, Optional
from .promptql_agent import PromptQLAgent

class AgentWrapper:
    """
    Wrapper for LLM agent APIs.
    This implementation uses the PromptQL API.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the agent wrapper with optional configuration.
        
        Args:
            config: A dictionary containing any configuration needed for your agent
                   (e.g., API endpoints, authentication, parameters)
        """
        self.config = config or {}
        self.promptql_agent = PromptQLAgent(self.config)
    
    def execute_query(self, query: str) -> str:
        """
        Execute a query on the PromptQL agent and return the response as a string.
        
        Args:
            query: The natural language query to send to the agent
            
        Returns:
            A string containing the agent's complete response
        """
        return self.promptql_agent.execute_query(query)
```

### 4. Configure Your PromptQL Project

#### Get Your PromptQL API Key

You can generate or retrieve your PromptQL API key using one of these methods:

- **From Hasura Console**: Navigate to your project settings page
- **Using DDN CLI**:
  ```bash
  ddn auth generate-promptql-secret-key  # Generate new key
  ddn auth print-promptql-secret-key     # Print existing key
  ```

#### Get Your DDN SQL Endpoint URL

**Important**: The DDN URL must be in the following format:
```
https://project-name.ddn.hasura.app/v1/sql
```

To find this URL:
1. Login to your DDN console
2. Navigate to your project
3. Go to the "Settings" or "API" section
4. Look for "SQL Endpoint URL" or copy the project URL and add `/v1/sql` to the end

### 5. Set Up Configuration Files

Create a `.env` file:
```bash
cp .env.example .env
nano .env
```

Add your API keys:
```
# API key for the reliability tool to use for evaluation
OPENAI_API_KEY=your_openai_api_key_here
# OR
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# PromptQL API key for the agent being tested
PROMPTQL_API_KEY=your_promptql_api_key_here
```

Create a `config.yaml` file:
```bash
cp config.yaml.example config.yaml
nano config.yaml
```

Configure it for PromptQL:
```yaml
# Choose which LLM provider to use for evaluation
llm_provider: "openai"  # or "anthropic"

# Choose which model to use
llm_model: "gpt-4o"  # or appropriate model

# PromptQL agent configuration
agent_config:
  api_url: "https://api.promptql.pro.hasura.io/query"
  ddn_url: "https://your-project-name.ddn.hasura.app/v1/sql"  # IMPORTANT: Use your actual DDN SQL endpoint
  timezone: "America/Los_Angeles"  # Set your preferred timezone
  llm_provider: "hasura"  # PromptQL's LLM provider

# Where to save the report
report_path: "./promptql_reliability_report.md"

# Advanced settings
advanced:
  repeat_count: 5  # Number of times to run each prompt
  max_tokens_per_call: 12000  # Max tokens for evaluation
```

### 6. Create Test Prompts

Create a YAML file with prompts that match your data model:
```bash
nano promptql_prompts.yaml
```

Example content:
```yaml
prompts:
  - id: "data_overview"
    text: "What data tables are available and what information do they contain?"
    description: "Schema discovery query"
  
  - id: "simple_query"
    text: "Show me all users from New York"
    description: "Basic filtering query"
  
  - id: "complex_analysis"
    text: "What's the month-over-month growth in transaction volume for the past 6 months?"
    description: "Time-series analysis with calculation"
    
  - id: "data_aggregation"
    text: "Show me the top 5 products by revenue and their respective categories"
    description: "Aggregation with join query"
    
  - id: "anomaly_detection"
    text: "Are there any unusual patterns in user signups over the past week?"
    description: "Open-ended analysis query"
```

**Important**: Customize these prompts to match your specific database schema and use cases.

### 7. Run the Reliability Test

```bash
poetry run agent-reliability promptql_prompts.yaml
```

## Understanding the Results

The tool will generate a detailed reliability report in Markdown format (`promptql_reliability_report.md` by default), evaluating:

1. **Visibility Score (1-10)**: How well PromptQL explains:
   - Which data sources it's using
   - Its reasoning steps
   - SQL queries being generated
   - Assumptions being made
   - Limitations of the analysis

2. **Repeatability Score (1-10)**: How consistently PromptQL:
   - Produces the same core answers
   - Uses the same reasoning approach
   - Accesses the same data sources
   - Produces consistent calculations
   - Maintains a consistent structure

3. **Overall Reliability Score**: Combined score from visibility and repeatability

## Example Report Output

Here's a snippet of what your reliability report might look like:

```markdown
# Agent Reliability Testing Report

## Overview

- **Date**: 2025-03-21 14:30:45
- **LLM Provider**: openai
- **LLM Model**: gpt-4o
- **Number of prompts tested**: 5

## Executive Summary

Below is an overview of the reliability testing results:

| Prompt ID | Prompt Description | Reliability Score |
|-----------|-------------------|-------------------|
| data_overview | Schema discovery query | 8.5 |
| simple_query | Basic filtering query | 9.0 |
| complex_analysis | Time-series analysis with calculation | 7.2 |
| data_aggregation | Aggregation with join query | 8.3 |
| anomaly_detection | Open-ended analysis query | 6.8 |

## Prompt: data_overview

**Query**: What data tables are available and what information do they contain?

### Executive Summary

PromptQL demonstrates strong reliability with an overall score of 8.5/10. The agent efficiently explores the database schema and clearly explains the available tables and their relationships.

### Visibility Analysis

Visibility Score: 9/10

Strengths:
- Clearly identifies all database tables queried
- Shows the SQL information schema query used to retrieve metadata
- Explains relationships between tables based on column names
- Provides a comprehensive overview of table structures

Weaknesses:
- Could provide more details about data types and constraints
```

## Troubleshooting Common Issues

### Authentication Errors
- Verify your PromptQL API key is correct
- Check that your `.env` file is properly formatted
- Ensure the `PROMPTQL_API_KEY` environment variable is being read correctly

### DDN URL Errors
- Double-check the DDN URL format: `https://project-name.ddn.hasura.app/v1/sql`
- Verify you're using the SQL endpoint URL, not just the project URL
- Test the URL directly to ensure it's accessible

### PromptQL Agent Implementation Errors
- Make sure the `promptql_agent.py` file is correctly placed in the `agent_reliability` directory
- Check for any Python import errors or syntax issues
- Verify that the agent wrapper is properly modified to use the PromptQL agent

### Schema-Related Errors
- Ensure your prompts reference tables and fields that actually exist in your database
- Start with basic schema discovery queries to understand what data is available

### LLM Provider Errors
- Verify your OpenAI or Anthropic API keys if you see evaluation errors
- Check that the specified model names are correct and available

## Next Steps

After receiving your reliability report:

1. **Identify problem areas** where visibility or repeatability scores are low
2. **Improve your prompts** to be more specific and aligned with your schema
3. **Compare different versions** of your PromptQL implementations
4. **Share feedback** with your team to improve overall reliability

By periodically testing reliability, you can ensure that your PromptQL-powered applications maintain high standards of visibility and repeatability, leading to better user experiences and more trustworthy AI-powered data systems.