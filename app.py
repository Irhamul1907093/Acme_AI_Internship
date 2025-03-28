from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
import pandas as pd

app = FastAPI()

# Database Connection
DATABASE_URL = "mysql+pymysql://root:pranjal@localhost:3306/budget_db"
engine = create_engine(DATABASE_URL)

@app.get("/")
def home():
    return {"message": "Welcome to the Budget Dashboard API"}

@app.get("/budget/summary")
def get_budget_summary():
    query = """
    SELECT 
        Subsidiary,
        Sector,
        SUM(Allocated_Budget) AS total_allocated,
        SUM(Spent_amount) AS total_spent,
        SUM(Remaining_Budget) AS total_remaining
    FROM budget_transactions
    GROUP BY Subsidiary, Sector;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query)).mappings().all()  # Convert result to dictionary format
    return result


@app.get("/budget/{subsidiary}")
def get_budget_by_subsidiary(subsidiary: str):
    query = """
    SELECT 
        sector,
        SUM(Allocated_Budget) AS total_allocated,
        SUM(Spent_Amount) AS total_spent,
        SUM(Remaining_Budget) AS total_remaining
    FROM budget_transactions
    WHERE subsidiary = :subsidiary
    GROUP BY sector;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"subsidiary": subsidiary}).mappings().all()
    if not result:
        raise HTTPException(status_code=404, detail="Subsidiary not found")
    return result

