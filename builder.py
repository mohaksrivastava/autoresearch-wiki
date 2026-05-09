import os
import yaml

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

def generate_mkdocs_config():
    config = {
        'site_name': 'Autoresearch Knowledge Base',
        'theme': {
            'name': 'material'
        },
        'plugins': [
            'search',
            'table-reader'
        ],
        'nav': [
            {'Home': 'index.md'},
            {'Audit Trail': 'audit_trail.md'}
        ]
    }

    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, sort_keys=False)

def write_llm_output(output_text, audit_trail_json_str=None):
    docs_dir = 'docs'
    ensure_dir(docs_dir)

    index_path = os.path.join(docs_dir, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

    if audit_trail_json_str:
        audit_path = os.path.join(docs_dir, 'audit_trail.md')
        with open(audit_path, 'w', encoding='utf-8') as f:
            f.write("# Audit Trail\n\n```json\n" + audit_trail_json_str + "\n```\n")

def build_site(llm_output, audit_trail_json_str=None):
    generate_mkdocs_config()
    write_llm_output(llm_output, audit_trail_json_str)
    print("Site config and output generated successfully.")

def rebuild_site():
    """Helper to just rebuild using subprocess"""
    import subprocess
    try:
        subprocess.run(["mkdocs", "build"], check=True)
        print("Successfully rebuilt site.")
    except subprocess.CalledProcessError as e:
        print(f"Error rebuilding site: {e}")
