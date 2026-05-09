import argparse
import subprocess
from ingestion import run_ingestion
from research_manager import run_agent_loop

def main():
    parser = argparse.ArgumentParser(description="Local Autoresearch and Knowledge Base CLI Framework")
    parser.add_argument("--input-dir", required=True, help="Directory containing documents to ingest")
    parser.add_argument("--question", required=True, help="Research question to ask the LLM")
    parser.add_argument("--model", required=True, choices=["anthropic", "gemini"], help="LLM model to use (anthropic or gemini)")

    args = parser.parse_args()

    print(f"Ingesting documents from {args.input_dir}...")
    extracted_text = run_ingestion(args.input_dir)

    if not extracted_text.strip():
        print("No text extracted from the provided directory.")
        return

    print("Orchestrating Agentic Autoresearcher...")
    run_agent_loop(extracted_text, args.question, args.model)

    print("\nSuccess! The static site has been generated with Audit Trail.")
    print("To view the site, run the following command:")
    print("  mkdocs serve")

if __name__ == "__main__":
    main()
