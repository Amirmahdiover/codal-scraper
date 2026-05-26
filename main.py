# main.py

import asyncio
import pandas as pd
from scraper.income_statement.link_collector import get_announcement_links
from scraper.income_statement.income_statement import extract_income_statement  # should be async too
from db.base import SessionLocal
from db.crud import insert_announcement
import asyncio
from scraper.explore_announcements import get_announcements

Codal_url='https://codal.ir/ReportList.aspx?search'



async def process_announcements():
    # Get announcements using async scraper
    async for ann in get_announcements(max_pages=1, delay_between=1.0):  # ⬅️ Adjust `max_pages`
        # Create DB session
        with SessionLocal() as db:
            try:
                insert_announcement(db, ann)
                print(f"[✅] Inserted: {ann['title']}")
            except Exception as e:
                print(f"[❌] Failed to insert: {ann['title']} | Error: {e}")




# # ------------------------------------income_statement.py----------------------------------
#     print('income_statement started!')
#     # --- Step 1. Collect links ---
#     links = await get_announcement_links(page_number=1)
#     print(f"🔗 Collected {len(links)} report links")

#     if not links:
#         print("⚠️ No links found.")
#         return

#     # --- Step 2. Extract data concurrently ---
#     tasks = [extract_income_statement(url) for url in links]
#     results = await asyncio.gather(*tasks, return_exceptions=True)

#     # --- Step 3. Combine valid DataFrames ---
#     dataframes = []
#     for url, df in zip(links, results):
#         if isinstance(df, pd.DataFrame) and not df.empty:
#             dataframes.append(df)
#         elif isinstance(df, Exception):
#             print(f"❌ Error in {url}: {df}")

#     # --- Step 4. Merge everything ---
#     if dataframes:
#         merged_df = pd.concat(dataframes, ignore_index=True)
#         merged_df.to_csv("merged_income_statements.csv", index=False, encoding="utf-8-sig")

#         print(f"✅ Saved merged_income_statements.csv ({len(merged_df)} rows total)")
#         print(merged_df.head())
#     else:
#         print("⚠️ No valid DataFrames extracted.")
# # ------------------------------------income_statement.py----------------------------------
from db.crud import insert_income_statement,get_audited_notsubtitles_income_statement_urls
from db.base import Base,engine
from datetime import datetime


# Global list to hold all records
all_income_statements = []

async def process_announcement(announcement: dict):
    url = announcement["url"]
    announcement_id = announcement["id"]

    df = await extract_income_statement(url, source_url=url, announcement_id=announcement_id)
    if df is not None:
        with SessionLocal() as db:
            insert_income_statement(db, df)


async def run_income_scraper(limit=50):
    with SessionLocal() as db:
        announcements = get_audited_notsubtitles_income_statement_urls(db, limit=limit)

    await asyncio.gather(*[process_announcement(ann) for ann in announcements])

# --- Run ---
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    asyncio.run(run_income_scraper(limit=50))

