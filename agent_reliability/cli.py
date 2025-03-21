"""
Command-line interface for the agent reliability testing tool.
"""
import os
import sys
import argparse
from dotenv import load_dotenv
from .reliability_tester import ReliabilityTester

def main():
    """Main CLI entry point for the agent reliability testing tool."""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    parser = argparse.ArgumentParser(
        description="Test the reliability of LLM agents"
    )
    
    parser.add_argument(
        "prompts_file",
        help="Path to the YAML file containing test prompts"
    )
    
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to configuration file (default: config.yaml)"
    )
    
    args = parser.parse_args()
    
    # Check if prompts file exists
    if not os.path.exists(args.prompts_file):
        print(f"Error: Prompts file not found: {args.prompts_file}")
        sys.exit(1)
    
    # Check if config file exists
    if not os.path.exists(args.config):
        print(f"Error: Configuration file not found: {args.config}")
        sys.exit(1)
    
    try:
        # Initialize and run the tester
        tester = ReliabilityTester(config_path=args.config)
        report = tester.run_tests(args.prompts_file)
        
        # Print report to console
        print("\n" + "="*80)
        print("AGENT RELIABILITY REPORT")
        print("="*80 + "\n")
        print(report)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()