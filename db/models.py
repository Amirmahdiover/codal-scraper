# db/models.py

from sqlalchemy import Column, Integer, String, Date, Boolean, BigInteger,Unicode,ForeignKey,Float,DateTime
from sqlalchemy.orm import relationship
from db.base import Base
from datetime import datetime

class Announcement(Base):
    __tablename__ = "announcements"

    announcement_type_id = Column(Integer, ForeignKey("announcement_types.id"))

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer)
    title = Column(Unicode(255))
    published_at = Column(Date)
    sent_at = Column(Date)
    tracing_no = Column(BigInteger)
    letter_code = Column(Unicode(20))
    symbol = Column(Unicode(250))
    url = Column(String)
    pdf_url = Column(String)
    excel_url = Column(String)
    attachment_url = Column(String)
    has_pdf = Column(Boolean)
    has_excel = Column(Boolean)
    has_html = Column(Boolean)
    is_estimate = Column(Boolean)
    # Add this if you want to access the full announcement type object
    announcement_type = relationship("AnnouncementType", back_populates="announcements")
    created_at = Column(DateTime, default=datetime.utcnow)
    # income_statement = relationship("IncomeStatement", back_populates="announcement", uselist=False)

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from db.base import Base  # Assuming you have your declarative base here

class CompanyType(Base):
    __tablename__ = "company_type"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class CompanyNature(Base):
    __tablename__ = "company_nature"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class PublisherStatus(Base):
    __tablename__ = "publisher_status"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class IndustryGroup(Base):
    __tablename__ = "industry_groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True)
    name = Column(Unicode(250), nullable=False, unique=True)
    ticker = Column(Unicode(250))
    created_at = Column(DateTime)

    external_id=Column(Integer,nullable=True)
    company_nature_id = Column(Integer, ForeignKey("company_nature.id"), nullable=True)
    company_type_id = Column(Integer, ForeignKey("company_type.id"), nullable=True)
    publisher_status_id = Column(Integer, ForeignKey("publisher_status.id"), nullable=True)
    industry_groups_id = Column(Integer, ForeignKey("industry_groups.id"), nullable=True)
    normalized_name = Column(Unicode(255))
    # Optionally add relationships (only if you want to join them later)
    # industry_group = relationship("IndustryGroup", back_populates="companies")


class AnnouncementGroup(Base):
    __tablename__ = 'announcement_groups'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    announcement_types = relationship("AnnouncementType", back_populates="group")


class AnnouncementType(Base):
    __tablename__ = 'announcement_types'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    group_id = Column(Integer, ForeignKey('announcement_groups.id'))

    group = relationship("AnnouncementGroup", back_populates="announcement_types")
    
    # back relationship
    announcements = relationship("Announcement", back_populates="announcement_type")


# --------------------------------------------------
# 🧠 Function: Add missing columns to DB dynamically
# --------------------------------------------------

from sqlalchemy import inspect, Column, String, Unicode, text
from sqlalchemy import create_engine


def sync_income_statement_columns(engine, label_map: dict):
    """
    Compares English labels (values from label_map) with IncomeStatement columns.
    Adds missing ones to the database as FLOAT columns.
    """

    # Reflect the current table structure
    insp = inspect(engine)
    existing_columns = {col['name'] for col in insp.get_columns("income_statements")}
    print(f"🔍 Existing columns: {existing_columns}")

    # Get unique English field names
    new_fields = set(label_map.values())

    # Find missing columns
    missing_fields = [field for field in new_fields if field not in existing_columns]
    print(f"⚠️ Missing columns to add: {missing_fields}")

    if not missing_fields:
        print("✅ No missing columns. Model is up to date.")
        return

    # Add missing columns dynamically to DB
    with engine.connect() as conn:
        for field in missing_fields:
            # All financial fields are usually numeric — FLOAT is safe default
            alter_stmt = text(f'ALTER TABLE income_statements ADD "{field}" NVARCHAR(250)')
            try:
                conn.execute(alter_stmt)
                print(f"✅ Added column: {field}")
            except Exception as e:
                print(f"❌ Error adding column {field}: {e}")
        conn.commit()

    print("🎉 Database structure updated successfully.")
