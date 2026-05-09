import os
import re
import yaml
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import PyPDF2
from docx import Document

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def ingest_pdf(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {filepath}: {e}")
    return text

def ingest_docx(filepath):
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Error reading DOCX {filepath}: {e}")
    return text

def ingest_html(filepath):
    text = ""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
            text = soup.get_text(separator='\n')
    except Exception as e:
        print(f"Error reading HTML {filepath}: {e}")
    return text

def ingest_xlsx(filepath, docs_data_dir):
    text_content = ""
    try:
        excel_file = pd.ExcelFile(filepath)
        filename = Path(filepath).stem
        for sheet_name in excel_file.sheet_names:
            df = excel_file.parse(sheet_name)
            # Make sure we generate valid filename
            safe_sheet_name = "".join([c if c.isalnum() else "_" for c in sheet_name])
            csv_filename = f"{filename}_{safe_sheet_name}.csv"
            csv_path = os.path.join(docs_data_dir, csv_filename)
            df.to_csv(csv_path, index=False)
            text_content += f"Spreadsheet data from {filename}, sheet {sheet_name} saved as CSV to {csv_path}.\n"
    except Exception as e:
        print(f"Error reading XLSX {filepath}: {e}")
    return text_content

def ingest_rmd(filepath):
    text_content = ""
    metadata = {}
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter
        yaml_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            try:
                metadata = yaml.safe_load(yaml_content)
            except yaml.YAMLError as e:
                print(f"Error parsing YAML in {filepath}: {e}")
            # Remove yaml frontmatter from content
            content = content[yaml_match.end():]

        # Explicitly preserve the R code chunks within standard markdown code blocks
        # R chunks look like ```{r ...} ... ```
        content = re.sub(r'^```\{r\s*.*?\}$', '```r', content, flags=re.MULTILINE)

        if metadata:
            text_content += f"Metadata: {metadata}\n\n"
        text_content += "Content:\n" + content + "\n"

    except Exception as e:
        print(f"Error reading Rmd {filepath}: {e}")
    return text_content

def run_ingestion(input_dir):
    docs_data_dir = os.path.join("docs", "assets", "data")
    ensure_dir(docs_data_dir)

    all_text = ""

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            filepath = os.path.join(root, file)
            ext = Path(filepath).suffix.lower()

            extracted_text = ""
            if ext == '.pdf':
                extracted_text = ingest_pdf(filepath)
            elif ext == '.docx':
                extracted_text = ingest_docx(filepath)
            elif ext == '.html':
                extracted_text = ingest_html(filepath)
            elif ext == '.xlsx':
                extracted_text = ingest_xlsx(filepath, docs_data_dir)
            elif ext == '.rmd':
                extracted_text = ingest_rmd(filepath)
            else:
                continue

            if extracted_text.strip():
                all_text += f"\n\n--- Document: {file} ---\n\n"
                all_text += extracted_text

    return all_text
