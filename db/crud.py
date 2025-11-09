from sqlalchemy.orm import Session
from db.models import Company, AnnouncementType,Announcement
from scraper.utils import extract_announcement_type_id,to_gregorian_datetime,normalize_persian_text


def get_or_create_company(db: Session, name: str, symbol: str = None):
    # we also normilizing here
    normalized = normalize_persian_text(name)

    company = db.query(Company).filter_by(normalized_name=normalized).first()
    if company:
        return company

    company = Company(name=name, ticker=symbol, normalized_name=normalized)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

# def get_or_create_company(db: Session, name: str, symbol: str = None):
#     company = db.query(Company).filter_by(name=name).first()
#     if company:
#         return company
    
#     company = Company(name=name, ticker=symbol)
#     db.add(company)
#     db.commit()
#     db.refresh(company)
#     return company


def get_announcement_type_by_id(db: Session, type_id: int):
    return db.query(AnnouncementType).filter_by(id=type_id).first()


def insert_announcement(db, raw_data):

    company = get_or_create_company(db, raw_data["company_name"], raw_data["symbol"])
        # Safely extract announcement type ID, fallback to -1
    try:
        ann_type_id = extract_announcement_type_id(raw_data["url"])
        if not isinstance(ann_type_id, int):
            raise ValueError("Invalid type ID")
    except Exception:
        ann_type_id = -1  # fallback
    published_at = to_gregorian_datetime(raw_data["published_at"])
    sent_at = to_gregorian_datetime(raw_data["sent_at"])
   
    ann = Announcement(
        title=raw_data["title"],
        company_id=company.id,
        announcement_type_id=ann_type_id,
        published_at=published_at,
        sent_at=sent_at,
        tracing_no=raw_data["tracing_no"],
        letter_code=raw_data["letter_code"],
        symbol=raw_data["symbol"],
        url=raw_data["url"],
        pdf_url=raw_data["pdf_url"],
        excel_url=raw_data["excel_url"],
        attachment_url=raw_data["attachment_url"],
        has_pdf=raw_data["has_pdf"],
        has_excel=raw_data["has_excel"],
        has_html=raw_data["has_html"],
        is_estimate=raw_data["is_estimate"],
    )
    db.add(ann)
    db.commit()

# crud.py
from db.auto_income import IncomeStatement
from sqlalchemy.exc import SQLAlchemyError
def insert_income_statement(db, record: dict):
    # Convert any Series to scalar values just in case
    cleaned_record = {k: (v.iloc[0] if hasattr(v, 'iloc') else v) for k, v in record.items()}

    try:
        stmt = IncomeStatement(**cleaned_record)
        db.add(stmt)
        db.commit()
        db.refresh(stmt)
        print("✅ Inserted income statement successfully.")
    except SQLAlchemyError as e:
        db.rollback()
        print(f"❌ Error inserting income statement: {e}")


def get_audited_notsubtitles_income_statement_urls(db: Session, limit: int = 100) -> list[str]:
    """
    Get announcement URLs whose title contains exactly one (حسابرسی شده) wrapped in ()
    and append &sheetId=1 to the URL.
    """
    results = (
        db.query(Announcement.id,Announcement.url, Announcement.title)
        .filter(
            Announcement.title.contains("حسابرسی شده"),
            Announcement.url.isnot(None)
        )
        .order_by(Announcement.published_at.desc())
        .limit(limit)
        .all()
    )

    filtered_urls_ids = []
    for ann_id,url, title in results:
        if title.count("(") == 1 and title.count(")") == 1:
            # Always append "&sheetId=1", even if other query params exist
            connector = "&" if "?" in url else "?"
            full_url = f"{url}{connector}sheetId=1"
            filtered_urls_ids.append({
                                    "id": ann_id,
                                    "url": full_url
                                })
    return filtered_urls_ids

from db.base_utils import get_model_fields