# link_collector.py

import aiohttp
import asyncio

async def get_announcement_links(page_number):
    """
    Asynchronously fetch Codal report URLs for a given page number from the Codal search API.

    Args:
        page_number (int): The page number to fetch.

    Returns:
        list: A list of full Codal report URLs (strings).
    """

    base_url = "https://codal.ir"
    api_url = "https://search.codal.ir/api/search/v2/q"

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
        "search": "true"
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, params=params, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

                report_links = []
                for letter in data.get("Letters", []):
                    relative_url = letter.get("Url")
                    if relative_url:
                        full_url = base_url + relative_url + "&sheetId=1"
                        report_links.append(full_url)

                return report_links

    except Exception as e:
        print(f"❌ Error fetching page {page_number}: {e}")
        return []
