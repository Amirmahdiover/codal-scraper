from __future__ import annotations

import argparse
import asyncio
import csv
import json
import re
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup


ROOT_DIR = Path(__file__).resolve().parents[1]

LABEL_MAP_PATH = ROOT_DIR / "scraper" / "income_statement" / "label_map.json"
OUTPUT_PATH = ROOT_DIR / "data" / "samples" / "income_statements_sample.csv"

SEARCH_API_URL = "https://search.codal.ir/api/search/v2/q"
BASE_SITE_URL = "https://codal.ir"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/html, */*",
}

TARGET_COLUMNS = [
    "company_name",
    "symbol",
    "title",
    "period_ended",
    "operating_revenues",
    "gross_profit",
    "operating_profit",
    "net_income",
    "eps",
    "source_url",
]

FIELD_ALIASES = {
    "operating_revenues": [
        "operating_revenues",
        "operating_revenue",
        "operating_income",
        "total_income",
        "income",
    ],
    "gross_profit": ["gross_profit"],
    "operating_profit": ["operating_profit"],
    "net_income": ["net_income", "net_income_cont_ops"],
    "eps": ["eps", "eps_net", "eps_operating"],
}


def normalize_persian_text(text: Any) -> str:
    if text is None:
        return ""

    text = str(text).strip()

    replacements = {
        "ي": "ی",
        "ك": "ک",
        "ى": "ی",
        "‌": "",
        "‍": "",
        "‏": "",
        "ـ": "",
        "،": ",",
        "–": "-",
        "—": "-",
    }

    for src, target in replacements.items():
        text = text.replace(src, target)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_digits(text: Any) -> str:
    return str(text).translate(
        str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
    )


def parse_amount(value: Any) -> Optional[float]:
    if value is None:
        return None

    if isinstance(value, (int, float)):
        return float(value)

    text = normalize_digits(value).strip()

    if text in {"", "-", "–", "—", "nan", "None"}:
        return None

    is_negative = text.startswith("(") and text.endswith(")")

    text = text.replace("(", "").replace(")", "")
    text = text.replace(",", "").replace("٬", "").replace("٫", ".")
    text = re.sub(r"[^\d\-.]", "", text)

    if text in {"", "-", ".", "-."}:
        return None

    try:
        number = float(text)
        return -abs(number) if is_negative else number
    except ValueError:
        return None


def load_label_map() -> dict[str, str]:
    with open(LABEL_MAP_PATH, "r", encoding="utf-8") as f:
        raw_map = json.load(f)

    return {
        normalize_persian_text(persian_label): english_field
        for persian_label, english_field in raw_map.items()
    }


def build_report_url(relative_url: str) -> str:
    full_url = urljoin(BASE_SITE_URL, relative_url)

    if "sheetId=" not in full_url:
        connector = "&" if "?" in full_url else "?"
        full_url = f"{full_url}{connector}sheetId=1"

    return full_url


def is_suitable_announcement(letter: dict[str, Any]) -> bool:
    title = normalize_persian_text(letter.get("Title", ""))

    has_url = bool(letter.get("Url"))
    has_financial_statement_words = "صورت" in title and "مالی" in title
    is_audited = "حسابرسی شده" in title and "حسابرسی نشده" not in title
    is_correction = "اصلاحیه" in title or "اصلاح" in title

    return has_url and has_financial_statement_words and is_audited and not is_correction


async def fetch_announcements_page(
    session: aiohttp.ClientSession,
    page_number: int,
) -> list[dict[str, Any]]:
    # These params are intentionally close to the existing project collector.
    # We filter report titles locally to avoid fragile CODAL API filters.
    params = {
        "Audited": "true",
        "AuditorRef": -1,
        "Category": 1,
        "Childs": "false",
        "CompanyState": -1,
        "CompanyType": -1,
        "Consolidatable": "true",
        "IsNotAudited": "false",
        "Length": -1,
        "LetterType": -1,
        "Mains": "true",
        "NotAudited": "false",
        "NotConsolidatable": "true",
        "PageNumber": page_number,
        "Publisher": "false",
        "ReportingType": -1,
        "TracingNo": -1,
        "search": "true",
    }

    async with session.get(SEARCH_API_URL, params=params, headers=HEADERS) as response:
        if response.status != 200:
            body = await response.text()
            print(f"[WARN] CODAL search page {page_number} returned HTTP {response.status}")
            print(body[:300])
            return []

        data = await response.json(content_type=None)
        return data.get("Letters", [])


async def collect_candidate_reports(
    session: aiohttp.ClientSession,
    max_pages: int,
    delay: float,
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for page_number in range(1, max_pages + 1):
        print(f"[INFO] Fetching CODAL search page {page_number}...")

        letters = await fetch_announcements_page(session, page_number)

        for letter in letters:
            if not is_suitable_announcement(letter):
                continue

            candidates.append(
                {
                    "company_name": letter.get("CompanyName"),
                    "symbol": letter.get("Symbol"),
                    "title": letter.get("Title"),
                    "source_url": build_report_url(letter.get("Url", "")),
                }
            )

        await asyncio.sleep(delay)

    return candidates


async def fetch_report_html(session: aiohttp.ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url, headers=HEADERS) as response:
            if response.status != 200:
                print(f"[WARN] Report returned HTTP {response.status}: {url}")
                return None

            return await response.text()
    except Exception as exc:
        print(f"[WARN] Failed to fetch report: {url} | {exc}")
        return None


def get_company_name_from_html(html: str) -> Optional[str]:
    soup = BeautifulSoup(html, "lxml")
    company_name = soup.find("span", id="ctl00_txbCompanyName")

    if company_name:
        return company_name.get_text(strip=True)

    return None


def extract_from_embedded_json(html: str) -> tuple[list[dict[str, Any]], Optional[str]]:
    match = re.search(r"var datasource\s*=\s*({[\w\W]+?});", html)

    if not match:
        return [], None

    try:
        data = json.loads(match.group(1), strict=False)
    except json.JSONDecodeError:
        return [], None

    period_ended = data.get("periodEndToDate")
    sheets = data.get("sheets", [])

    for sheet in sheets:
        for table in sheet.get("tables", []):
            cells = table.get("cells", [])

            labels_by_row: dict[str, str] = {}
            values_by_row: dict[str, Any] = {}

            for cell in cells:
                if cell.get("cellGroupName") != "Body":
                    continue

                if cell.get("isVisible") is not True:
                    continue

                row_code = str(cell.get("rowCode"))
                column_code = str(cell.get("columnCode"))
                value = cell.get("value")

                if column_code == "1":
                    labels_by_row[row_code] = normalize_persian_text(value)
                elif column_code == "2":
                    values_by_row[row_code] = value

            rows: list[dict[str, Any]] = []

            for row_code, label in labels_by_row.items():
                if not label:
                    continue

                rows.append(
                    {
                        "label": label,
                        "amount": parse_amount(values_by_row.get(row_code)),
                    }
                )

            if rows:
                return rows, period_ended

    return [], period_ended


def extract_from_html_table(html: str) -> tuple[list[dict[str, Any]], Optional[str]]:
    soup = BeautifulSoup(html, "lxml")

    period_ended = None
    header_cell = soup.find("th", class_="GridHeader YearColumn CurrentPeriodHeader")

    if header_cell:
        date_span = header_cell.find("span")
        if date_span:
            period_ended = date_span.get_text(strip=True)

    rows: list[dict[str, Any]] = []

    for tr in soup.find_all("tr", class_=["SimpleRow", "ComputationalRow", "GroupHeader"]):
        label_cell = tr.find("td", class_="DescriptionColumn")
        value_cell = tr.find("td", class_="GridItem YearColumn CurrentPeriod")

        if not label_cell or not value_cell:
            continue

        label = normalize_persian_text(label_cell.get_text(strip=True))

        input_tag = value_cell.find("input")
        if input_tag:
            amount_raw = input_tag.get("value", "")
        else:
            amount_raw = value_cell.get_text(strip=True)

        if label:
            rows.append(
                {
                    "label": label,
                    "amount": parse_amount(amount_raw),
                }
            )

    return rows, period_ended


def normalize_financial_rows(
    rows: list[dict[str, Any]],
    label_map: dict[str, str],
) -> dict[str, Optional[float]]:
    record: dict[str, Optional[float]] = {}

    for row in rows:
        label = normalize_persian_text(row.get("label"))
        field_name = label_map.get(label)

        if not field_name:
            continue

        if field_name not in record or record[field_name] is None:
            record[field_name] = row.get("amount")

    return record


def coalesce(record: dict[str, Any], aliases: list[str]) -> Any:
    for alias in aliases:
        value = record.get(alias)

        if value is not None and value != "":
            return value

    return None


async def build_sample_rows(
    candidates: list[dict[str, Any]],
    session: aiohttp.ClientSession,
    label_map: dict[str, str],
    limit: int,
    delay: float,
) -> list[dict[str, Any]]:
    sample_rows: list[dict[str, Any]] = []
    seen_urls: set[str] = set()

    for candidate in candidates:
        if len(sample_rows) >= limit:
            break

        source_url = candidate["source_url"]

        if source_url in seen_urls:
            continue

        seen_urls.add(source_url)

        print(f"[INFO] Extracting: {candidate.get('symbol')} | {candidate.get('title')}")

        html = await fetch_report_html(session, source_url)
        if not html:
            continue

        rows, period_ended = extract_from_embedded_json(html)

        if not rows:
            rows, period_ended = extract_from_html_table(html)

        if not rows:
            print("[WARN] No income statement rows extracted.")
            await asyncio.sleep(delay)
            continue

        normalized_record = normalize_financial_rows(rows, label_map)

        output_row = {
            "company_name": get_company_name_from_html(html) or candidate.get("company_name"),
            "symbol": candidate.get("symbol"),
            "title": candidate.get("title"),
            "period_ended": period_ended,
            "operating_revenues": coalesce(
                normalized_record,
                FIELD_ALIASES["operating_revenues"],
            ),
            "gross_profit": coalesce(
                normalized_record,
                FIELD_ALIASES["gross_profit"],
            ),
            "operating_profit": coalesce(
                normalized_record,
                FIELD_ALIASES["operating_profit"],
            ),
            "net_income": coalesce(
                normalized_record,
                FIELD_ALIASES["net_income"],
            ),
            "eps": coalesce(
                normalized_record,
                FIELD_ALIASES["eps"],
            ),
            "source_url": source_url,
        }

        has_useful_metric = any(
            output_row[column] is not None
            for column in [
                "operating_revenues",
                "gross_profit",
                "operating_profit",
                "net_income",
                "eps",
            ]
        )

        if has_useful_metric:
            sample_rows.append(output_row)
            print(f"[OK] Added sample row {len(sample_rows)}/{limit}")
        else:
            print("[WARN] Extracted rows, but target metrics were empty.")

        await asyncio.sleep(delay)

    return sample_rows


def write_csv(rows: list[dict[str, Any]]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=TARGET_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create a small public CODAL income statement CSV sample for portfolio use."
    )
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--max-pages", type=int, default=5)
    parser.add_argument("--delay", type=float, default=1.2)

    args = parser.parse_args()

    label_map = load_label_map()

    timeout = aiohttp.ClientTimeout(total=45)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        candidates = await collect_candidate_reports(
            session=session,
            max_pages=args.max_pages,
            delay=args.delay,
        )

        print(f"[INFO] Candidate audited reports found: {len(candidates)}")

        rows = await build_sample_rows(
            candidates=candidates,
            session=session,
            label_map=label_map,
            limit=args.limit,
            delay=args.delay,
        )

    if not rows:
        raise RuntimeError(
            "No sample rows were created. Try increasing --max-pages or relaxing filters."
        )

    write_csv(rows)

    print(f"[DONE] Saved {len(rows)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    asyncio.run(main())