"""
Example agent implementation that calls a REST API.
"""
import requests
import json
import os
from typing import Dict, Any

class SimpleAPIAgent:
    """
    Example agent implementation that calls a REST API.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the agent with configuration.
        
        Args:
            config: Configuration dictionary containing API details
        """
        self.api_url = config.get("api_url", "https://your-agent-api.com/query")
        self.api_key = config.get("api_key", os.environ.get("AGENT_API_KEY"))
        self.parameters = config.get("parameters", {})
    
    def execute_query(self, query: str) -> str:
        """
        Execute a query on the agent API and return the response as a string.
        
        Args:
            query: The natural language query to send to the agent
            
        Returns:
            A string containing the agent's complete response
        """
        response = requests.post(
            self.api_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            json={
                "query": query,
                "parameters": self.parameters
            }
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

# Example usage:
# To use this in the agent_wrapper.py file:
#
# from examples.agent_example import SimpleAPIAgent
#
# def execute_query(self, query: str) -> str:
#     agent = SimpleAPIAgent(self.config)
#     return agent.execute_query(query)