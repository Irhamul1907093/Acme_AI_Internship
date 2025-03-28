
import pandas as pd
from sqlalchemy import create_engine

# Load the dataset (CSV file)
df = pd.read_csv("dataset_company_budget_allocation_dashboard.csv")

# Create the SQLAlchemy engine to connect to MySQL
DATABASE_URL = "mysql+pymysql://root:pranjal@localhost:3306/budget_db"
engine = create_engine(DATABASE_URL)

# Insert data into MySQL (if table exists)
df.to_sql("budget_transactions", con=engine, if_exists="append", index=False)

print("Data inserted successfully!")
