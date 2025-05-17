import os
import requests
from airtable import Airtable
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_table_name(base_id, table_id, api_key):
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
                return table['name']
    return "Recipe Collection"  # Fallback to generic name if we can't get the real one

def fetch_airtable_data():
    # Get Airtable credentials from environment variables
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_id = os.getenv('AIRTABLE_TABLE_NAME')  # This is actually the table ID
    api_key = os.getenv('AIRTABLE_API_KEY')
    
    if not all([base_id, table_id, api_key]):
        raise ValueError("Missing required environment variables. Please set AIRTABLE_BASE_ID, AIRTABLE_TABLE_NAME, and AIRTABLE_API_KEY")
    
    # Get the actual table name
    table_name = get_table_name(base_id, table_id, api_key)
    
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
    return records, table_name

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
    try:
        records, table_name = fetch_airtable_data()
        generate_html(records, table_name)
        print("Successfully generated index.html")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 