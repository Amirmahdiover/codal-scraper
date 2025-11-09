# db/auto_income.py
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from db.base import engine

Base = automap_base()
Base.prepare(engine, reflect=True)

IncomeStatement = Base.classes.income_statements