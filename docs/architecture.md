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