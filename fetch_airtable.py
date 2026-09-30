import os
import hashlib
import json
import requests
from airtable import Airtable
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_table_metadata(base_id, table_id, api_key):
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        tables = response.json()['tables']
        for table in tables:
            if table['id'] == table_id:
                return table
    response.raise_for_status()
    raise ValueError(f"Table {table_id!r} was not found in base {base_id!r}")

def fetch_airtable_data():
    # Get Airtable credentials from environment variables
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_id = os.getenv('AIRTABLE_TABLE_NAME')  # This is actually the table ID
    api_key = os.getenv('AIRTABLE_API_KEY')
    
    if not all([base_id, table_id, api_key]):
        raise ValueError("Missing required environment variables. Please set AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, and AIRTABLE_API_KEY")
    
    # Get the actual table name
    table = get_table_metadata(base_id, table_id, api_key)
    
    # Initialize Airtable client
    airtable = Airtable(base_id, table_id, api_key=api_key)
    
    # Fetch all records
    records = airtable.get_all()
    
    # Sort records by name/title
    def get_sort_key(record):
        fields = record['fields']
        for field_name in ['Name', 'Title', 'name', 'title']:
            if field_name in fields:
                return fields[field_name].lower()
        return ''  # Default to empty string if no name/title found
    
    records.sort(key=get_sort_key)
    return records, table


def meaningful_record(record, fields_by_name):
    """Return stable source data, excluding formula results and expiring URLs."""
    fields = {}
    for name, value in record['fields'].items():
        field_type = fields_by_name.get(name, {}).get('type')
        if field_type == 'formula':
            continue
        if field_type == 'multipleAttachments':
            value = [
                {key: attachment.get(key) for key in ('id', 'filename', 'size', 'type')}
                for attachment in value
            ]
        fields[name] = value
    return {'id': record['id'], 'fields': fields}


def content_hash(records, table, template_path='template.html'):
    """Hash only changes that should cause a new public deployment."""
    fields_by_name = {field['name']: field for field in table.get('fields', [])}
    payload = {
        'table_name': table['name'],
        # Including the schema catches formula-definition and empty-field changes,
        # while excluding each formula's evaluated result avoids clock-driven noise.
        'schema': table.get('fields', []),
        'records': [meaningful_record(record, fields_by_name) for record in records],
    }
    digest = hashlib.sha256()
    digest.update(json.dumps(payload, sort_keys=True, separators=(',', ':')).encode())
    with open(template_path, 'rb') as template_file:
        digest.update(template_file.read())
    return digest.hexdigest()

def generate_html(records, table_name):
    # Set up Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    template = env.get_template('template.html')
    
    # Render template with records and table name
    html_content = template.render(records=records, table_name=table_name)
    
    # Write to output file
    with open('index.html', 'w') as f:
        f.write(html_content)

def main():
    records, table = fetch_airtable_data()
    generate_html(records, table['name'])
    with open('content-hash.txt', 'w') as hash_file:
        hash_file.write(content_hash(records, table) + '\n')
    print("Successfully generated index.html and content-hash.txt")

if __name__ == "__main__":
    main()
