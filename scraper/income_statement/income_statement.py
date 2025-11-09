# data_filter_extractor.py

import aiohttp
import pandas as pd
import json
import re
from bs4 import BeautifulSoup
from datetime import datetime

headers = {
    "User-Agent": "Mozilla/5.0"
}

def get_company_name(html):
    soup = BeautifulSoup(html, 'html.parser')
    company_name = soup.find('span', id='ctl00_txbCompanyName')
    return company_name.text.strip() if company_name else "نامشخص"


def try_parse_date_or_number(val: str):
    """Returns datetime if val is a date, else numeric if possible."""
    if re.fullmatch(r"\d{4}/\d{2}/\d{2}", val):
        try:
            return datetime.strptime(val, "%Y/%m/%d")
        except ValueError:
            return val
    try:
        return float(val)
    except ValueError:
        return val


def extract_from_json(html: str) -> pd.DataFrame | None:
    """Extracts income statement from embedded JS JSON."""
    pattern = re.compile(r"var datasource\s*=\s*({[\w\W]+?});")
    match = pattern.search(html)
    if not match:
        return None

    try:
        json_str = match.group(1)
        data = json.loads(json_str)


        period_end = data.get("periodEndToDate")


        sheets = data.get("sheets", [])
        if not sheets or not sheets[0].get("tables"):
            return None

        table = sheets[0]["tables"][0]
        cells = table.get("cells", [])
        df = pd.DataFrame(cells)
        df = df[(df['cellGroupName'] == 'Body') & (df['isVisible'] == True)]

        labels = df[df['columnCode'] == 1][['rowCode', 'value']].rename(columns={'value': 'label'})
        values = df[df['columnCode'] == 2][['rowCode', 'value']].rename(columns={'value': 'amount'})

        income_df = pd.merge(labels, values, on='rowCode', how='inner')
        income_df['amount'] = (
            income_df['amount']
            .str.replace(',', '', regex=False)
            .str.replace('(', '-', regex=False)
            .str.replace(')', '', regex=False)
        )
        income_df['amount'] = income_df['amount'].apply(try_parse_date_or_number)
        income_df['company_name'] = get_company_name(html)
        income_df['periodEndToDate'] = period_end
        return income_df
    except Exception as e:
        print(f"❌ Error extracting from JSON: {e}")
        return None


def extract_from_html_table(html: str) -> pd.DataFrame | None:
    """Fallback: Extracts income statement from visible HTML table."""
    try:
        soup = BeautifulSoup(html, 'lxml')
        data_rows = []

        header_cell = soup.find("th", class_="GridHeader YearColumn CurrentPeriodHeader")
        if header_cell:
            date_span = header_cell.find("span")
            report_date = date_span.get_text(strip=True) if date_span else "تاریخ نامشخص"
        else:
            report_date = "تاریخ نامشخص"

        for row in soup.find_all("tr", class_=["SimpleRow", "ComputationalRow", "GroupHeader"]):
            description_tag = row.find("td", class_="DescriptionColumn")
            if not description_tag:
                continue

            description = description_tag.get_text(strip=True)
            current_value_tag = row.find("td", class_="GridItem YearColumn CurrentPeriod")
            current_value = (
                current_value_tag.find("input").get("value", "").strip()
                if current_value_tag and current_value_tag.find("input")
                else ""
            )

            data_rows.append({
                "label": description,
                f"amount as of {report_date}": current_value
            })

        if not data_rows:
            return None

        df = pd.DataFrame(data_rows)
        value_col = df.columns[1]
        df[value_col] = (
            df[value_col]
            .str.replace(',', '', regex=False)
            .str.replace('(', '-', regex=False)
            .str.replace(')', '', regex=False)
        )
        df[value_col] = df[value_col].apply(try_parse_date_or_number)
        df['company_name'] = get_company_name(html)
        return df

    except Exception as e:
        print(f"❌ Error extracting from HTML table: {e}")
        return None


from .postprocess import convert_df_to_record

async def extract_income_statement(url: str, source_url: str="", announcement_id: int=0) -> pd.DataFrame | None:
    """
    Asynchronously extracts income statement from a Codal report (either from embedded JSON or fallback HTML).
    """
    try:
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print(f"❌ HTTP {response.status} for {url}")
                    return None
                html = await response.text()

        df = extract_from_json(html)
        if df is not None:
            print(f"✅ Extracted using JSON datasource: {url}")
            return convert_df_to_record(df, source_url, announcement_id)


        df = extract_from_html_table(html)
        if df is not None:
            print(f"🔁 Extracted from HTML table: {url}")
            return convert_df_to_record(df, source_url, announcement_id)


        print(f"⚠️ No data extracted from: {url}")
        return None

    except Exception as e:
        print(f"❌ Error fetching or parsing {url}: {e}")
        return None


# Optional: for standalone test
if __name__ == "__main__":
    import asyncio

    test_url = "https://codal.ir/Reports/Decision.aspx?LetterSerial=fKr0O6UkKY4UAIlFBLcOnw%3d%3d&rt=8&let=6&ct=0&ft=-1"

    async def test():
        df = await extract_income_statement(test_url)
        if df is not None:
            print(df)
            labels = df['label'].dropna().unique().tolist()
            labels = pd.DataFrame(labels,columns=["label"])
            labels.to_csv('sharif_abad.csv',index=False)
        else:
            print("No income statement found.")

    asyncio.run(test())
