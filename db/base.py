from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import urllib.parse

# Load environment variables from .env
load_dotenv()

# Read from environment variables
DB_CONFIG = {
    'driver': os.getenv('DB_DRIVER'),
    'server': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'username': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD'),
    'trust_cert': os.getenv('TRUST_SERVER_CERTIFICATE', 'no'),
    'use_windows_auth': os.getenv('USE_WINDOWS_AUTH', 'no')
}

# Build connection string
if DB_CONFIG['use_windows_auth'].lower() == 'yes':
    # Windows Authentication
    connection_string = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate={DB_CONFIG['trust_cert']};"
    )
else:
    # SQL Server Authentication
    connection_string = (
        f"DRIVER={{{DB_CONFIG['driver']}}};"
        f"SERVER={DB_CONFIG['server']};"
        f"DATABASE={DB_CONFIG['database']};"
        f"UID={DB_CONFIG['username']};"
        f"PWD={DB_CONFIG['password']};"
        f"TrustServerCertificate={DB_CONFIG['trust_cert']};"
        f"CHARSET=UTF8;"
    )

params = urllib.parse.quote_plus(connection_string)

# Create SQLAlchemy engine
engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}",connect_args={"unicode_results": True}, echo=False, future=True)

# Create a configured session class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base
Base = declarative_base()
