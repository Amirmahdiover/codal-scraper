from sqlalchemy.orm import Session
from db.models import Company, AnnouncementType,Announcement
from scraper.utils import extract_announcement_type_id,to_gregorian_datetime,normalize_persian_text


def get_or_create_company(db: Session, name: str, symbol: str = None):
    normalized = normalize_persian_text(name)

    company = db.query(Company).filter_by(normalized_name=normalized).first()
    if company:
        return company

    company = Company(name=name, ticker=symbol, normalized_name=normalized)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company

def get_or_create_company(db: Session, name: str, symbol: str = None):
    company = db.query(Company).filter_by(name=name).first()
    if company:
        return company
    
    company = Company(name=name, ticker=symbol)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


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