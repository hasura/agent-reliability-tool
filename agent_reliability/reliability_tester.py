"""
Main class for testing agent reliability.
"""
import os
import yaml
import time
from typing import Dict, Any, List, Optional
import re
from .agent_wrapper import AgentWrapper
from .llm_client import LLMClient

class ReliabilityTester:
    """Main class for testing agent reliability."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the reliability tester.
        
        Args:
            config_path: Path to the configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize LLM client
        self.llm_client = LLMClient(
            provider=self.config["llm_provider"],
            model=self.config["llm_model"]
        )
        
        # Initialize agent wrapper
        self.agent = AgentWrapper(config=self.config.get("agent_config", {}))
        
        # Get advanced settings
        self.repeat_count = self.config["advanced"]["repeat_count"]
        self.max_tokens_per_call = self.config["advanced"]["max_tokens_per_call"]
        
        # Load evaluation prompts
        self._initialize_prompts()
    
    def _initialize_prompts(self):
        """Initialize the evaluation prompts."""
        # Visibility prompt template
        self.visibility_prompt = """
You are an expert evaluator of AI agent reliability. Your task is to evaluate the visibility of an agent's response.

Visibility means how clearly the agent explains its process, assumptions, and data sources.

Please analyze the following user query and agent response:

USER QUERY:
{query}

AGENT RESPONSE:
{response}

Evaluate the response on a scale of 1-10 for visibility, considering:
1. Does the agent clearly indicate what data sources it's using?
2. Does the agent explain its reasoning steps?
3. Does the agent make its assumptions explicit?
4. Would a user understand how conclusions were reached?
5. Does the agent provide enough context to understand the scope of its answer?
6. Is it clear what tools or functions the agent might be using?
7. If calculations were performed, are they shown or explained?
8. If there are limitations in the response, are they acknowledged?
9. Would a domain expert be able to verify the agent's work based on what's shown?
10. Does the agent show evidence of its information retrieval or generation process?

Please provide your evaluation in this format:
- Visibility Score: [1-10]
- Strengths: [list what the agent does well for visibility]
- Weaknesses: [list where the agent could improve visibility]
- Detailed Analysis: [your analysis of the visibility]
"""
        
        # Repeatability prompt template
        self.repeatability_prompt = """
You are an expert evaluator of AI agent reliability. Your task is to evaluate the repeatability of an agent's responses.

Repeatability means how consistent the agent's responses are when given the same input multiple times.

Please analyze the following user query and the 5 agent responses to that same query:

USER QUERY:
{query}

RESPONSE 1:
{response_1}

RESPONSE 2:
{response_2}

RESPONSE 3:
{response_3}

RESPONSE 4:
{response_4}

RESPONSE 5:
{response_5}

Evaluate the consistency on a scale of 1-10 for repeatability, considering:
1. Do the core answers remain the same across responses?
2. Are there any contradictions between responses?
3. If there are differences, are they explained by randomness that's part of the agent's process?
4. Do all responses use similar reasoning approaches?
5. Are data sources consistent across responses?
6. If calculations are performed, do they yield similar results?
7. Is the structure and format of responses consistent?
8. Are the steps taken by the agent consistent across responses?
9. If there are variations, would they lead to different user decisions?
10. Is the level of detail consistent across responses?

Please provide your evaluation in this format:
- Repeatability Score: [1-10]
- Consistency Analysis: [analysis of how consistent the responses are]
- Notable Differences: [highlight any important differences between responses]
- Impact Assessment: [how differences might impact user trust or decision-making]
"""
        
        # Combined report prompt template
        self.report_prompt = """
You are an expert evaluator of AI agent reliability. Please create a comprehensive reliability report based on the visibility and repeatability evaluations.

VISIBILITY EVALUATION:
{visibility_evaluation}

REPEATABILITY EVALUATION:
{repeatability_evaluation}

Create a reliability report with these sections:
1. Executive Summary: Brief overview of the agent's reliability with an overall score out of 10 (equal weighting between visibility and repeatability).
2. Visibility Analysis: Detailed assessment of how well the agent explains its process.
3. Repeatability Analysis: Detailed assessment of the agent's consistency.
4. Key Reliability Issues: Most important problems affecting reliability.
5. Recommendations: Specific suggestions to improve the agent's reliability.
6. Conclusion: Final thoughts on trustworthiness and usability.

For the overall reliability score, calculate it as: (Visibility Score + Repeatability Score) / 2

IMPORTANT: Always clearly state the overall reliability score in this exact format: "Overall Reliability Score: X.X/10" (where X.X is the numerical score).

The report should be formatted in Markdown and be detailed enough to help the tester understand their agent's strengths and weaknesses.
"""
    
    def load_prompts(self, prompts_path: str) -> List[Dict[str, str]]:
        """
        Load test prompts from a YAML file.
        
        Args:
            prompts_path: Path to the YAML file with prompts
            
        Returns:
            List of prompt dictionaries (limited to the first 5)
        """
        with open(prompts_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Take only the first 5 prompts
        return data.get("prompts", [])[:5]
    
    def evaluate_visibility(self, query: str, response: str) -> str:
        """
        Evaluate the visibility of an agent's response.
        
        Args:
            query: The user query
            response: The agent's response
            
        Returns:
            Visibility evaluation text
        """
        prompt_data = {
            "query": query,
            "response": response
        }
        
        return self.llm_client.chunk_and_process(
            self.visibility_prompt, 
            prompt_data,
            self.max_tokens_per_call
        )
    
    def evaluate_repeatability(self, query: str, responses: List[str]) -> str:
        """
        Evaluate the repeatability of an agent's responses.
        
        Args:
            query: The user query
            responses: List of agent responses to the same query
            
        Returns:
            Repeatability evaluation text
        """
        prompt_data = {
            "query": query,
            "response_1": responses[0],
            "response_2": responses[1],
            "response_3": responses[2],
            "response_4": responses[3],
            "response_5": responses[4]
        }
        
        return self.llm_client.chunk_and_process(
            self.repeatability_prompt, 
            prompt_data,
            self.max_tokens_per_call
        )
    
    def generate_report(self, visibility_eval: str, repeatability_eval: str) -> str:
        """
        Generate a comprehensive reliability report.
        
        Args:
            visibility_eval: Visibility evaluation text
            repeatability_eval: Repeatability evaluation text
            
        Returns:
            Markdown-formatted reliability report
        """
        prompt_data = {
            "visibility_evaluation": visibility_eval,
            "repeatability_evaluation": repeatability_eval
        }
        
        return self.llm_client.chunk_and_process(
            self.report_prompt, 
            prompt_data,
            self.max_tokens_per_call
        )
    
    def test_prompt(self, prompt: Dict[str, str]) -> Dict[str, Any]:
        """
        Test a single prompt for reliability.
        
        Args:
            prompt: Dictionary containing prompt information
            
        Returns:
            Dictionary with test results
        """
        query = prompt["text"]
        
        print(f"\nTesting prompt: {prompt.get('id', 'Unknown')} - {query[:50]}...")
        
        # Test visibility
        print("  Testing visibility...")
        response = self.agent.execute_query(query)
        visibility_evaluation = self.evaluate_visibility(query, response)
        
        # Test repeatability
        print(f"  Testing repeatability ({self.repeat_count} runs)...")
        responses = []
        for i in range(self.repeat_count):
            print(f"    Run {i+1}/{self.repeat_count}...")
            responses.append(self.agent.execute_query(query))
            # Add a small delay to avoid rate limiting
            time.sleep(1)
        
        repeatability_evaluation = self.evaluate_repeatability(query, responses)
        
        # Generate report
        print("  Generating reliability report...")
        report = self.generate_report(visibility_evaluation, repeatability_evaluation)
        
        return {
            "prompt": prompt,
            "visibility_evaluation": visibility_evaluation,
            "repeatability_evaluation": repeatability_evaluation,
            "report": report
        }
    
    def run_tests(self, prompts_path: str) -> str:
        """
        Run reliability tests on a set of prompts.
        
        Args:
            prompts_path: Path to the YAML file with prompts
            
        Returns:
            Markdown-formatted comprehensive report
        """
        prompts = self.load_prompts(prompts_path)
        
        if not prompts:
            return "Error: No prompts found in the specified file."
        
        print(f"Running reliability tests on {len(prompts)} prompts...")
        
        all_results = []
        for prompt in prompts:
            results = self.test_prompt(prompt)
            all_results.append(results)
        
        # Combine all reports into a single comprehensive report
        combined_report = self._combine_reports(all_results)
        
        # Save report to file
        report_path = self.config.get("report_path", "agent_reliability_report.md")
        with open(report_path, 'w') as f:
            f.write(combined_report)
        
        print(f"\nReliability report saved to: {report_path}")
        
        return combined_report
    
    def _combine_reports(self, results: List[Dict[str, Any]]) -> str:
        """
        Combine individual prompt reports into a comprehensive report.
        
        Args:
            results: List of test results
            
        Returns:
            Combined markdown report
        """
        report = "# Agent Reliability Testing Report\n\n"
        report += f"## Overview\n\n"
        report += f"- **Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"- **LLM Provider**: {self.config['llm_provider']}\n"
        report += f"- **LLM Model**: {self.config['llm_model']}\n"
        report += f"- **Number of prompts tested**: {len(results)}\n\n"
        
        # Add executive summary section
        report += "## Executive Summary\n\n"
        report += "Below is an overview of the reliability testing results:\n\n"
        report += "| Prompt ID | Prompt Description | Reliability Score |\n"
        report += "|-----------|-------------------|-------------------|\n"
        
        for result in results:
            prompt_id = result["prompt"].get("id", "Unknown")
            prompt_desc = result["prompt"].get("description", result["prompt"]["text"][:30] + "...")
            
            # Extract score from report
            score_patterns = [
                r"overall score.*?(\d+(?:\.\d+)?)/10",
                r"overall score.*?(\d+(?:\.\d+)?)",
                r"reliability score.*?(\d+(?:\.\d+)?)/10",
                r"reliability score.*?(\d+(?:\.\d+)?)",
                r"score of (\d+(?:\.\d+)?)/10",
                r"score of (\d+(?:\.\d+)?)"
            ]

            score = "N/A"
            for pattern in score_patterns:
                score_match = re.search(pattern, result["report"], re.IGNORECASE)
                if score_match:
                    score = score_match.group(1)
                    break
            
            report += f"| {prompt_id} | {prompt_desc} | {score} |\n"
        
        report += "\n"
        
        # Add individual prompt reports
        for result in results:
            prompt_id = result["prompt"].get("id", "Unknown")
            report += f"## Prompt: {prompt_id}\n\n"
            report += f"**Query**: {result['prompt']['text']}\n\n"
            report += result["report"]
            report += "\n\n---\n\n"
        
        return report