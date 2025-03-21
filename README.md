# Agent Reliability Testing Tool

A tool for testing and understanding the reliability of LLM Agents. This tool evaluates agents on two key dimensions:

1. **Visibility**: How well the agent explains what it's doing
2. **Repeatability**: How consistent the agent's responses are

## Quick Start

```bash
# Clone the repository
git clone https://github.com/hasura/agent-reliability-tool.git
cd agent-reliability-tool

# Set up configuration
cp config.yaml.example config.yaml
cp .env.example .env

# Edit .env to add your API keys
nano .env  # Add your OpenAI or Anthropic API key

# Edit config.yaml to configure settings
nano config.yaml  # Choose LLM provider and model

# Install dependencies
poetry install

# Run the tool
poetry run agent-reliability examples/test_prompts.yaml
```

## Installation

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/hasura/agent-reliability-tool.git
   cd agent-reliability-tool
   ```

2. Install dependencies using Poetry:
   ```bash
   poetry install
   ```

3. Copy the example configuration files:
   ```bash
   cp config.yaml.example config.yaml
   cp .env.example .env
   ```

4. Edit the `.env` file to add your API keys:
   ```
   # For OpenAI
   OPENAI_API_KEY=your_openai_api_key_here
   
   # For Anthropic
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

5. Edit the `config.yaml` file to configure your LLM provider choice and other settings:
   ```yaml
   # Choose your LLM provider
   llm_provider: "anthropic"  # or "openai"
   
   # Choose the specific model
   llm_model: "claude-3-sonnet-20240229"  # or appropriate OpenAI model
   ```

## Implementing Your Agent

1. Open `agent_reliability/agent_wrapper.py`
2. Replace the implementation of the `execute_query` method with your agent's API call
3. Configure any necessary parameters in the `config.yaml` file under the `agent_config` section

Example agent implementation:

```python
def execute_query(self, query: str) -> str:
    """Execute a query on your agent and return the response as a string."""
    response = requests.post(
        self.config.get("api_url", "https://your-agent-api.com/query"),
        headers={
            "Authorization": f"Bearer {self.config.get('api_key')}",
            "Content-Type": "application/json"
        },
        json={"query": query, "parameters": self.config.get("parameters", {})}
    )
    
    if response.status_code != 200:
        return f"Error: Agent API returned status code {response.status_code}"
    
    result = response.json()
    
    # Combine multiple response components if present
    final_response = ""
    if "answer" in result:
        final_response += f"ANSWER:\n{result['answer']}\n\n"
    if "reasoning" in result:
        final_response += f"REASONING:\n{result['reasoning']}\n\n"
    if "code" in result:
        final_response += f"CODE:\n{result['code']}\n\n"
    if "sources" in result:
        final_response += f"SOURCES:\n{json.dumps(result['sources'], indent=2)}\n\n"
    
    return final_response.strip()
```

## Creating Test Prompts

Create a YAML file containing the prompts you want to test. Only the first 5 prompts will be used.

Example:

```yaml
prompts:
  - id: "factual_query"
    text: "What is the capital of France?"
    description: "Basic factual query"
  
  - id: "data_analysis"
    text: "I have sales data for Q1: Jan=$10,000, Feb=$12,500, Mar=$9,800. What's the trend and Q1 average?"
    description: "Simple data analysis and calculation"
  
  # More prompts...
```

## Running the Tests

```bash
poetry run agent-reliability your_prompts.yaml
```

Or if you prefer to run it directly:

```bash
python -m agent_reliability.cli your_prompts.yaml
```

## Understanding the Report

The reliability report includes:

1. **Executive Summary**: Overall reliability score and high-level assessment
2. **Visibility Analysis**: How well the agent explains its process
3. **Repeatability Analysis**: How consistent the agent's responses are
4. **Key Reliability Issues**: Most important problems affecting reliability
5. **Recommendations**: Suggestions for improving reliability
6. **Conclusion**: Overall trustworthiness assessment

The report is saved as a Markdown file (default: `agent_reliability_report.md`) and also printed to the console.

## How Reliability is Evaluated

### Visibility Criteria (10-point scale)
1. Clear indication of data sources
2. Explanation of reasoning steps
3. Explicit assumptions
4. Understandable conclusions
5. Sufficient context
6. Clear indication of tools/functions used
7. Explanations of calculations
8. Acknowledgment of limitations
9. Verifiability by domain experts
10. Evidence of information retrieval process

### Repeatability Criteria (10-point scale)
1. Consistency of core answers
2. Absence of contradictions
3. Explainable variations
4. Consistency of reasoning approaches
5. Consistency of data sources
6. Consistency of calculation results
7. Consistency of response structure
8. Consistency of steps taken
9. Impact of variations on user decisions
10. Consistency of detail level

The overall reliability score is the average of the visibility and repeatability scores.

## Configuration Options

In `config.yaml`:

- `llm_provider`: LLM provider for evaluation ("openai" or "anthropic")
- `llm_model`: Specific model to use
- `agent_config`: Configuration for your agent
- `report_path`: Path to save the reliability report
- `advanced.repeat_count`: Number of repetitions for repeatability testing
- `advanced.max_tokens_per_call`: Maximum tokens per LLM call

## Technical Notes

- This tool uses direct HTTP API calls to OpenAI and Anthropic instead of their client libraries to avoid potential proxy-related issues.
- The report generation is designed to handle large responses through summarization when necessary.
- The tool is designed to be extensible - you can modify the evaluation prompts in the `reliability_tester.py` file to adjust the criteria.

## Example Files

The repository includes example files to help you get started:

- `examples/test_prompts.yaml`: Example test prompts
- `examples/agent_example.py`: Example agent implementation

## Guides for Specific Agents

The following guides provide specific instructions for testing different LLM agents:

- [Using the Reliability Tool with PromptQL](docs/promptql-guide.md) - Guide for testing Hasura PromptQL implementations

## License

[MIT License](LICENSE)