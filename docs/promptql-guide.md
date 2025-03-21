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

### 3. Configure Your PromptQL Project

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

### 4. Set Up Configuration Files

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

### 5. Create Test Prompts

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

### 6. Run the Reliability Test

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

## Troubleshooting Common Issues

### Authentication Errors
- Verify your PromptQL API key is correct
- Check that your `.env` file is properly formatted
- Ensure the `PROMPTQL_API_KEY` environment variable is being read correctly

### DDN URL Errors
- Double-check the DDN URL format: `https://project-name.ddn.hasura.app/v1/sql`
- Verify you're using the SQL endpoint URL, not just the project URL
- Test the URL directly to ensure it's accessible

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
