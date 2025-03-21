"""
Client for interacting with language model APIs (OpenAI or Anthropic) using direct HTTP requests.
"""
import os
import json
import requests
from typing import Dict, Any, Optional

class LLMClient:
    """Client for interacting with language model APIs using direct HTTP requests."""
    
    def __init__(self, provider: str, model: str):
        """
        Initialize the LLM client.
        
        Args:
            provider: The LLM provider ("openai" or "anthropic")
            model: The specific model to use
        """
        self.provider = provider.lower()
        self.model = model
        
        # Validate provider and API key
        if self.provider == "openai":
            self.api_key = os.environ.get("OPENAI_API_KEY")
            if not self.api_key:
                raise ValueError("OPENAI_API_KEY environment variable is required")
            self.api_url = "https://api.openai.com/v1/chat/completions"
        elif self.provider == "anthropic":
            self.api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY environment variable is required")
            self.api_url = "https://api.anthropic.com/v1/messages"
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_text(self, prompt: str, max_tokens: int = 4000) -> str:
        """
        Generate text using the selected LLM provider and model.
        
        Args:
            prompt: The prompt to send to the LLM
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text from the LLM
        """
        if self.provider == "openai":
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens
            }
            
            # Make direct API call
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            # Check for errors
            if response.status_code != 200:
                raise Exception(f"OpenAI API error ({response.status_code}): {response.text}")
            
            # Parse response
            result = response.json()
            return result["choices"][0]["message"]["content"]
        
        elif self.provider == "anthropic":
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            data = {
                "model": self.model,
                "max_tokens": max_tokens,
                "messages": [{"role": "user", "content": prompt}]
            }
            
            # Make direct API call
            response = requests.post(
                self.api_url,
                headers=headers,
                json=data
            )
            
            # Check for errors
            if response.status_code != 200:
                raise Exception(f"Anthropic API error ({response.status_code}): {response.text}")
            
            # Parse response
            result = response.json()
            return result["content"][0]["text"]
    
    def chunk_and_process(self, prompt_template: str, 
                          content: Dict[str, str], 
                          max_tokens_per_chunk: int = 12000) -> str:
        """
        Handle large content by chunking and processing in parts.
        
        Args:
            prompt_template: The template for the prompt with {placeholders}
            content: Dictionary with content to insert into the template
            max_tokens_per_chunk: Maximum tokens per chunk
            
        Returns:
            Concatenated response from all chunks
        """
        # Generate the full prompt
        prompt = prompt_template.format(**content)
        
        # Rough token estimate (4 chars ≈ 1 token)
        estimated_tokens = len(prompt) / 4
        
        if estimated_tokens <= max_tokens_per_chunk:
            # If it fits, process directly
            return self.generate_text(prompt)
        
        # If too large, first generate summaries of large content items
        summarized_content = {}
        for key, value in content.items():
            if len(value) > 8000:  # If item is large (roughly 2000 tokens)
                summary_prompt = f"Please summarize the following content concisely while preserving all key information:\n\n{value}"
                summarized_content[key] = self.generate_text(summary_prompt, max_tokens=2000)
            else:
                summarized_content[key] = value
        
        # Generate new prompt with summarized content
        summarized_prompt = prompt_template.format(**summarized_content)
        
        # Add note about summarization
        summarized_prompt = "Note: Some parts of the content have been summarized for processing.\n\n" + summarized_prompt
        
        return self.generate_text(summarized_prompt)