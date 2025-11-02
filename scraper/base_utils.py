# scraper/base_utils.py

import aiohttp

async def fetch_html(url: str, headers: dict = None) -> str | None:
    """
    Asynchronously fetches HTML content from the specified URL.

    Args:
        url (str): The target URL to fetch.
        headers (dict, optional): Optional headers for the HTTP request.

    Returns:
        str | None: The HTML content as a string, or None if request fails.
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0"
    }

    headers = headers or default_headers

    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    print(f"❌ Failed to fetch {url} (status {response.status})")
                    return None
    except Exception as e:
        print(f"❌ Exception while fetching {url}: {e}")
        return None
