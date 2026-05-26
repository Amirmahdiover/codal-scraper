# Architecture Overview

This project collects CODAL announcements, extracts income statement data from report pages, normalizes Persian financial labels into English fields, and prepares the result for database or CSV/JSON output.

```mermaid
flowchart TD
    A[CODAL Website/API] --> B[Async Announcement Scraper]
    B --> C[Report URL Collector]
    C --> D[Income Statement Extractor]
    D --> E{Data Source}
    E --> F[Embedded JSON Parser]
    E --> G[HTML Table Fallback]
    F --> H[Persian Label Normalizer]
    G --> H
    H --> I[Clean Financial Fields]
    I --> J[SQL Server / CSV / JSON Output]






# Project Architecture

This project follows a simple scraping-to-output pipeline:

```text
CODAL Website / API
        ↓
Async Announcement Scraper
        ↓
Report URL Collector
        ↓
Income Statement Extractor
        ↓
JSON Parser / HTML Table Fallback
        ↓
Persian Label Normalizer
        ↓
Database / CSV / JSON Output
Main Components
1. Announcement Scraper

Collects financial announcement metadata from CODAL using async HTTP requests.

2. Income Statement Extractor

Fetches individual report pages and extracts income statement data.

3. Parser Layer

The parser first tries to extract structured data from embedded JSON.
If JSON data is not available, it falls back to parsing HTML tables.

4. Normalization Layer

Persian financial labels are normalized and mapped into English field names.

5. Storage / Output Layer

Cleaned records can be stored in a database or exported as CSV/JSON sample outputs.