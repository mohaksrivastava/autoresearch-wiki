import argparse
import subprocess
from ingestion import run_ingestion
from llm_orchestrator import run_llm
from builder import build_site

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

    print("Orchestrating LLM...")
    llm_output = run_llm(extracted_text, args.question, args.model)

    print("Building MkDocs site...")
    build_site(llm_output)

    print("Running mkdocs build...")
    try:
        subprocess.run(["mkdocs", "build"], check=True)
        print("\nSuccess! The static site has been generated.")
        print("To view the site, run the following command:")
        print("  mkdocs serve")
    except subprocess.CalledProcessError as e:
        print(f"Error running mkdocs build: {e}")
    except FileNotFoundError:
        print("Error: mkdocs is not installed or not found in PATH.")

if __name__ == "__main__":
    main()
