# CODAL Financial Reports Scraper

A Python web scraping and data pipeline project for collecting, parsing, normalizing, and exporting public financial report data from CODAL.

This project was built as a real-world web scraping portfolio project to demonstrate data extraction, data cleaning, financial label normalization, and structured output generation using Python.

---

## Overview

CODAL is a public financial disclosure platform. This project collects financial announcements and extracts structured income statement data from report pages.

The scraper can:

- Collect financial announcements from CODAL
- Extract income statement data from report pages
- Parse embedded JSON data when available
- Use HTML table extraction as a fallback
- Normalize Persian financial labels into English field names
- Store cleaned data in a database
- Prepare sample outputs for CSV/JSON/database use

---

## Features

- Asynchronous scraping with `aiohttp`
- Pagination support
- Configurable scraping limit
- JSON-based financial report extraction
- HTML table fallback parser
- Persian text normalization
- Persian/Jalali date conversion
- Financial label mapping
- SQLAlchemy database layer
- Sample output structure for portfolio/demo use
> Note: The sample CSV uses synthetic English demo data for portfolio presentation. The scraper itself is designed to extract and normalize financial statements from CODAL reports.
---

## Tech Stack

- Python
- aiohttp
- BeautifulSoup
- pandas
- SQLAlchemy
- SQL Server
- python-dotenv
- jdatetime

---

## Project Structure

```text
codal-scraper/
│
├── db/
│   ├── base.py
│   ├── crud.py
│   ├── models.py
│   └── auto_income.py
│
├── scraper/
│   ├── explore_announcements.py
│   ├── utils.py
│   │
│   └── income_statement/
│       ├── income_statement.py
│       ├── link_collector.py
│       ├── normalizer.py
│       ├── postprocess.py
│       └── label_map.json
│
├── data/
│   └── samples/
│
├── docs/
│
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
````

---

## How It Works

```text
CODAL Website/API
        ↓
Announcement Scraper
        ↓
Report Link Collector
        ↓
Income Statement Parser
        ↓
Label Normalizer
        ↓
Database / CSV / JSON Output
```

---

## Configuration

Create a `.env` file based on `.env.example`:

```env
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_HOST=localhost,1433
DB_NAME=Codal_db
DB_USER=your_username
DB_PASSWORD=your_password

TRUST_SERVER_CERTIFICATE=yes
USE_WINDOWS_AUTH=no

OPENROUTER_API_KEY=your_optional_api_key
```

Do not commit your real `.env` file.

---

## Quick Start

Clone the repository:

```bash
git clone https://github.com/Amirmahdiover/codal-scraper.git
cd codal-scraper
```

Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment file:

```bash
copy .env.example .env
```

Run the scraper demo:

```bash
python main.py
```

---

## Sample Output

Sample files are stored in:

```text
data/samples/
```

Example fields:

```text
company_name
symbol
title
period_ended
operating_revenues
gross_profit
net_income
eps
source_url
```

---

## Portfolio Purpose

This project demonstrates my ability to build real-world Python web scraping pipelines that:

* Extract data from public websites
* Handle different page structures
* Clean and normalize raw data
* Store data in a structured format
* Prepare outputs for business or analytical use

It can be used as a portfolio example for Python web scraping, data extraction, and data cleaning services.

---

## Ethical Scraping Note

This project is designed for working with public financial data. It does not bypass login systems, CAPTCHA, private data restrictions, or security mechanisms.

Scraping should always be done responsibly with reasonable request limits and respect for website terms.

