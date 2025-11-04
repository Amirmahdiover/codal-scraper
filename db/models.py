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
    income_statement = relationship("IncomeStatement", back_populates="announcement", uselist=False)

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


class IncomeStatement(Base):
    __tablename__ = "income_statements"

    id = Column(Integer, primary_key=True)
    company_name = Column(Unicode(250))
    source_url = Column(Unicode(1000))
    period_ended = Column(String(100))
    announcement_id = Column(Integer, ForeignKey("announcements.id"), nullable=False, unique=True)


    cost_of_operating_revenues = Column(String(50))
    operating_revenues = Column(String(50))
    current_year = Column(String(50))
    previous_years = Column(String(50))
    other_revenues = Column(String(50))
    non_operating_revenues_and_expenses = Column(String(50))
    other_expenses = Column(String(50))
    capital = Column(String(50))
    net_profit_loss_discontinued_ops = Column(String(50))
    net_profit_loss_per_share_rial = Column(String(50))
    net_profit_loss = Column(String(50))
    net_profit_loss_continuing_ops = Column(String(50))
    profit_loss_continuing_before_tax = Column(String(50))
    operating_profit_loss = Column(String(50))
    gross_profit_loss = Column(String(50))
    basic_earnings_loss_per_share = Column(String(50))
    basic_earnings_loss_per_share_colon = Column(String(50))
    continuing_operations_colon = Column(String(50))
    discontinued_operations_colon = Column(String(50))
    operating_rial = Column(String(50))
    non_operating_rial = Column(String(50))
    from_continuing_operations = Column(String(50))
    from_discontinued_operations = Column(String(50))
    income_tax_expense = Column(String(50))
    impairment_expense_on_receivables_exceptional = Column(String(50))
    selling_admin_general_expenses = Column(String(50))
    financial_expenses = Column(String(50))
    total_revenues = Column(String(50))
    total_expenses = Column(String(50))
    revenues = Column(String(50))
    unrealized_gain_loss_on_securities = Column(String(50))
    gain_loss_on_sale_of_securities = Column(String(50))
    profit_loss_before_financial_expenses = Column(String(50))
    fixed_income_or_expected_security_profit = Column(String(50))
    dividend_income = Column(String(50))
    commission_expense_for_entities = Column(String(50))
    expenses = Column(String(50))
    financial_costs = Column(String(50))
    total_operating_revenues = Column(String(50))
    total_operating_expenses = Column(String(50))
    financial_income = Column(String(50))
    commission_and_fee_income = Column(String(50))
    other_non_operating_income_and_expenses = Column(String(50))
    investment_profit_loss = Column(String(50))
    profit_loss_before_tax = Column(String(50))
    rental_expense = Column(String(50))
    depreciation_expense = Column(String(50))
    salary_wages_and_benefits_expense = Column(String(50))
    operating_expenses = Column(String(50))
    changes_in_other_technical_reserves = Column(String(50))
    ceded_reinsurance_premium = Column(String(50))
    net_retained_premium = Column(String(50))
    reinsurer_share_of_claims = Column(String(50))
    gross_paid_claims_and_benefits = Column(String(50))
    net_paid_claims_and_benefits = Column(String(50))
    gross_premium_income = Column(String(50))
    investment_income_from_insurance_resources = Column(String(50))
    insurance_income = Column(String(50))
    other_operating_income_and_expenses = Column(String(50))
    other_insurance_income = Column(String(50))
    other_insurance_expenses = Column(String(50))
    gross_profit_loss_from_insurance_activities = Column(String(50))
    income_tax = Column(String(50))
    participation_share_expense = Column(String(50))
    administrative_and_general_expenses = Column(String(50))
    insurance_expenses = Column(String(50))
    other_non_operating_misc_items = Column(String(50))
    other_non_operating_investment_income = Column(String(50))
    net_profit_loss_from_continuing_operations = Column(String(50))
    operating_income = Column(String(50))
    net_loss = Column(String(50))
    operating_loss = Column(String(50))
    gross_loss = Column(String(50))
    net_profit = Column(String(50))
    operating_profit = Column(String(50))
    gross_profit = Column(String(50))
    earnings_per_share = Column(String(50))
    guaranteed_interest_income = Column(String(50))
    impairment_loss_on_receivables = Column(String(50))
    gain_loss_from_investment_valuation_change = Column(String(50))
    gain_loss_on_sale_of_investments = Column(String(50))
    basic_earnings_loss_per_share_rial = Column(String(50))
    salaries_wages_benefits_expense = Column(String(50))
    announcement = relationship("Announcement", back_populates="income_statement")