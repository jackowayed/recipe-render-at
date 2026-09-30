# Airtable Static View Generator

This project generates a responsive static webpage from an Airtable view.

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project root with your Airtable credentials:

```
AIRTABLE_API_KEY=your_api_key_here
AIRTABLE_BASE_ID=your_base_id_here
AIRTABLE_TABLE_NAME=your_table_name_here
```

You can find these values in your Airtable account:

- API Key: https://airtable.com/account
- Base ID: Found in the API documentation when you click on your base
- Table Name: The name of the table you want to display

## Usage

Run the script to generate the static webpage:

```bash
python fetch_airtable.py
```

This will create an `index.html` file that you can open in any web browser. The page is fully responsive and will work well on both desktop and mobile devices.

It also creates `content-hash.txt`, a deployment fingerprint which ignores Airtable
formula results and expiring attachment URLs. The GitHub Actions workflow checks
that fingerprint weekly and skips the `gh-pages` update (and therefore the Pages
build) when only those volatile values changed. Run the workflow manually after an
Airtable edit if you do not want to wait for the weekly check; its `force_deploy`
option can also refresh formula output without a meaningful-data change.

## Features

- Responsive grid layout
- Card-based design
- Mobile-friendly
- Automatic handling of different field types
- Clean, modern styling
