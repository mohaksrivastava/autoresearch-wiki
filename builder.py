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
            {'Home': 'index.md'}
        ]
    }

    with open('mkdocs.yml', 'w') as f:
        yaml.dump(config, f, sort_keys=False)

def write_llm_output(output_text):
    docs_dir = 'docs'
    ensure_dir(docs_dir)

    index_path = os.path.join(docs_dir, 'index.md')
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(output_text)

def build_site(llm_output):
    generate_mkdocs_config()
    write_llm_output(llm_output)
    print("Site config and output generated successfully.")
