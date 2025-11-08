# import requests
# import pandas as pd
# headers = {
#     "User-Agent": "Mozilla/5.0"
# }
# url = "https://search.codal.ir/api/search/v1/companies"
# response = requests.get(url,headers=headers)
# data = response.json()

# # Optional: view a sample
# print(data[:3])

# df = pd.DataFrame(data)

# # Rename columns to match your SQL Server schema
# df = df.rename(columns={
#     "sy": "ticker",
#     "n": "name",
#     "i": "company_id",
#     "t":"publisher_status_id",
#     "st": "company_type_id", # company_type in url
#     "IG": "industry_groups_id",
#     "RT": "company_nature_id"
# })

# # Add fixed columns
# df["created_at"] = pd.Timestamp.now()
# df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
# df["audited"] = False

# df.to_csv("output/companies_cleaned.csv", index=False, encoding='utf-8-sig')


# -----------importing to sql----------------

import pandas as pd
from sqlalchemy import create_engine
import urllib
from sqlalchemy.dialects.mssql import NVARCHAR, INTEGER, DATETIME, BIT

# === Configuration ===
csv_path = r"C:\Users\amirmahdi\Desktop\codal scraper\output\companies_cleaned.csv"
server = 'localhost,1433'  # Port must be explicitly specified if using Docker
database = 'Codal_db'
username = 'sa'
password = 'Str0ngP@ssw0rd!'
table_name = 'companies'

# === Build connection string ===
params = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 18 for SQL Server}};"
    f"SERVER={server};"
    f"DATABASE={database};"
    f"UID={username};"
    f"PWD={password};"
    f"TrustServerCertificate=yes;"
    f"Encrypt=no;"
)

engine = create_engine(f"mssql+pyodbc:///?odbc_connect={params}")

# === Read and insert CSV ===
df = pd.read_csv(csv_path, encoding='utf-8')
df.to_sql(table_name, con=engine, if_exists='append', index=False,dtype={
    'name': NVARCHAR(200),
    'ticker': NVARCHAR(250),
    'company_id': INTEGER,
    'publisher_status_id': INTEGER,
    'company_type_id': INTEGER,
    'industry_groups_id': INTEGER,
    'company_nature_id': INTEGER,
    'created_at': DATETIME,
    'audited': BIT,
    })

print("✅ CSV data imported into SQL Server successfully.")
