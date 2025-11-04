import aiohttp
import asyncio
from typing import AsyncGenerator, Dict, Any

BASE_API_URL = "https://search.codal.ir/api/search/v2/q"
BASE_FILE_URL = "https://www.codal.ir"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json",
}

# ----------- Async Announcement Scraper Generator -----------

async def get_announcements(
    max_pages: int = 5, 
    concurrency: int = 5,
    delay_between: float = 0.5,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Async generator that fetches announcements from CODAL API with pagination.

    :param max_pages: Total number of pages to scrape.
    :param concurrency: Max number of concurrent requests.
    :param delay_between: Delay (in seconds) between page fetches to avoid rate limiting.
    :yield: Dict with announcement fields.
    """
    semaphore = asyncio.Semaphore(concurrency)

    async def fetch_page(session: aiohttp.ClientSession, page_number: int):
        url = BASE_API_URL
        params = {
            "PageNumber": page_number,
            "search": "true",
            "Audited": "false",
            "Childs": "true",
            "Consolidatable": "true",
            "NotAudited": "true",
            "NotConsolidatable": "true",
            "Mains": "true",
            "Length": "-1",
            "Category": "-1",
        }
        # params = {
        #     "Audited": "true",
        #     "AuditorRef": "-1",
        #     "Category": "1",
        #     "Childs": "false",
        #     "CompanyState": "-1",
        #     "CompanyType": "-1",
        #     "Consolidatable": "true",
        #     "IsNotAudited": "false",
        #     "Length": "-1",
        #     "LetterType": "6",
        #     "Mains": "true",
        #     "NotAudited": "false",
        #     "NotConsolidatable": "true",
        #     "PageNumber": "1",
        #     "Publisher": "false",
        #     "ReportingType": "-1",
        #     "TracingNo": "-1",
        #     "search": "true"
        # }
        async with semaphore:
            try:
                async with session.get(url, headers=HEADERS, params=params, timeout=15) as response:
                    if response.status != 200:
                        print(f"[❌] Page {page_number}: Status {response.status}")
                        return []
                    data = await response.json()
                    return data.get("Letters", [])
            except Exception as e:
                print(f"[⚠️] Page {page_number}: Error {e}")
                return []

    async with aiohttp.ClientSession() as session:
        for page in range(1, max_pages + 1):
            print(f"[🔎] Fetching page {page}...")
            letters = await fetch_page(session, page)

            if not letters:
                print("[ℹ️] No more announcements or failed request.")
                break

            for item in letters:
                yield {
                    "tracing_no": item.get("TracingNo"),
                    "symbol": item.get("Symbol"),
                    "company_name": item.get("CompanyName"),
                    "title": item.get("Title"),
                    "letter_code": item.get("LetterCode"),
                    "published_at": item.get("PublishDateTime"),   # Jalali (raw string)
                    "sent_at": item.get("SentDateTime"),           # Jalali (raw string)
                    "url": BASE_FILE_URL + item.get("Url", ""),
                    "pdf_url": BASE_FILE_URL + "/" + item.get("PdfUrl") if item.get("HasPdf") else None,
                    "excel_url": item.get("ExcelUrl") if item.get("HasExcel") else None,
                    "attachment_url": BASE_FILE_URL + item.get("AttachmentUrl") if item.get("HasAttachment") else None,
                    "has_pdf": item.get("HasPdf", False),
                    "has_excel": item.get("HasExcel", False),
                    "has_html": item.get("HasHtml", False),
                    "is_estimate": item.get("IsEstimate", False)
                }

            # wait before next page to avoid hammering the server
            await asyncio.sleep(delay_between)
