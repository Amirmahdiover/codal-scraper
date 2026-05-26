# Project Structure

```text
codal-scraper/
├── scraper/
│   ├── announcement/
│   ├── income_statement/
│   │   ├── extractor.py
│   │   ├── label_map.json
│   │   └── normalizer.py
│   └── utils/
├── db/
│   ├── base.py
│   └── models.py
├── scripts/
│   └── create_income_sample_csv.py
├── data/
│   └── samples/
│       ├── announcements_sample.csv
│       └── income_statements_sample.csv
├── docs/
│   ├── architecture.md
│   ├── fiverr_portfolio.md
│   └── screenshots/
├── main.py
├── requirements.txt
├── .env.example
└── README.md