import os
import anthropic
import google.generativeai as genai

def generate_prompt(question, text_content):
    return f"""You are a research assistant. Synthesize the following extracted text from various documents to answer the user's question.

Instructions:
1. Answer the question based ONLY on the provided text.
2. Format your response entirely in valid Markdown.
3. If the text mentions spreadsheet data saved as CSV to a path in docs/assets/data/, please link the CSV tables using markdown links or mention them clearly.
4. Include any useful insights derived from R code chunks or statistical models mentioned in the text.

User Question: {question}

Extracted Text:
{text_content}
"""

def call_anthropic(prompt):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

    client = anthropic.Anthropic(api_key=api_key)

    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=4000,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.content[0].text

def call_gemini(prompt):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content(prompt)
    return response.text

def run_llm(text_content, question, model_choice):
    prompt = generate_prompt(question, text_content)

    print(f"Calling LLM with model choice: {model_choice}...")
    if model_choice.lower() == "anthropic":
        return call_anthropic(prompt)
    elif model_choice.lower() == "gemini":
        return call_gemini(prompt)
    else:
        raise ValueError(f"Unknown model choice: {model_choice}. Use 'anthropic' or 'gemini'.")
