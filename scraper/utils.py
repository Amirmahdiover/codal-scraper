from urllib.parse import urlparse, parse_qs

def extract_announcement_type_id(url: str):
    try:
        parsed = urlparse(url)
        query = parse_qs(parsed.query)
        let_id = query.get('let')
        if let_id:
            return int(let_id[0])
    except Exception:
        pass
    return None


import jdatetime
from datetime import datetime

def to_gregorian_datetime(jalali_str: str):
    if not jalali_str:
        return None
    try:
        # Example: '۱۴۰۴/۰۸/۱۰ ۰۸:۵۳:۴۴'
        jalali_str = jalali_str.strip().replace("‌", "")
        # convert Persian digits → English
        trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
        jalali_str = jalali_str.translate(trans)

        date_part, time_part = jalali_str.split(" ")
        y, m, d = map(int, date_part.split("/"))
        h, mi, s = map(int, time_part.split(":"))
        g = jdatetime.datetime(y, m, d, h, mi, s).togregorian()
        return datetime(g.year, g.month, g.day, g.hour, g.minute, g.second)
    except Exception as e:
        print(f"[⚠️] Date conversion failed for {jalali_str}: {e}")
        return None


import re

# Persian name normalization
def normalize_persian_text(text: str) -> str:
    if not text:
        return ""
    
    text = text.strip().lower()

    replacements = {
        "ي": "ی",
        "ك": "ک",
        # "‌": "",     # ZWNJ
        "‍": "",     # ZWJ
        "ـ": "",     # Tatweel
        "،": ",",
        "“": "\"", "”": "\"",  # Quotation mark normalization
        "‘": "'", "’": "'",
    }

    for src, target in replacements.items():
        text = text.replace(src, target)

    # Collapse multiple spaces to one
    text = re.sub(r"\s+", " ", text)

    return text

def safe_float(value):
    """Convert a value to float if possible, else return None."""
    try:
        if value in ("", None, " ", "NaN"):
            return None
        return float(value)
    except (ValueError, TypeError):
        return None