from fastapi import FastAPI, HTTPException, Depends
from typing import Literal
import firebase_admin
from firebase_admin import credentials, db

app = FastAPI()

# 🔹 Initialize Firebase
cred = credentials.Certificate("firebase-adminsdk.json")  # Ensure this file is in your project folder
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://budgetdb-7d811-default-rtdb.firebaseio.com/'  # Replace with your actual URL
})

# 🔹 Define User Roles
USER_ROLES = {
    "admin": {"can_edit": True, "can_view": True},
    "viewer": {"can_edit": False, "can_view": True}
}


def get_user_role(role: Literal["admin", "viewer"]):
    """Checks if the user role is valid and returns role permissions."""
    if role not in USER_ROLES:
        raise HTTPException(status_code=403, detail="Invalid user role")
    return USER_ROLES[role]


@app.get("/")
def home():
    return {"message": "Welcome to the Budget Dashboard API"}


# 1️⃣ **Fetch total budget summary (Admin & Viewer)**
@app.get("/budget/summary")
def get_budget_summary(user_role: dict = Depends(lambda: get_user_role("viewer"))):
    ref = db.reference("/budget_transactions")
    transactions = ref.get()

    if not transactions:
        raise HTTPException(status_code=404, detail="No budget data available")

    summary = {}

    # 🔹 Iterate over the list instead of using `.items()`
    for record in transactions:
        if not isinstance(record, dict):
            continue  # Ignore invalid entries

        subsidiary = record.get("Subsidiary", "Unknown")
        sector = record.get("Sector", "Unknown")

        if (subsidiary, sector) not in summary:
            summary[(subsidiary, sector)] = {"total_allocated": 0, "total_spent": 0, "total_remaining": 0}

        summary[(subsidiary, sector)]["total_allocated"] += record.get("Allocated_Budget", 0)
        summary[(subsidiary, sector)]["total_spent"] += record.get("Spent_Amount", 0)
        summary[(subsidiary, sector)]["total_remaining"] += record.get("Remaining_Budget", 0)

    return [{"Subsidiary": sub, "Sector": sec, **vals} for (sub, sec), vals in summary.items()]


# 2️⃣ **Fetch budget by subsidiary (Admin & Viewer)**
@app.get("/budget/subsidiary/{subsidiary}")
def get_budget_by_subsidiary(subsidiary: str, user_role: dict = Depends(lambda: get_user_role("viewer"))):
    ref = db.reference("/budget_transactions")
    transactions = ref.get()

    if not transactions:
        raise HTTPException(status_code=404, detail="No budget data available")

    summary = {}

    for record in transactions:
        if isinstance(record, dict) and record.get("Subsidiary") == subsidiary:
            sector = record.get("Sector", "Unknown")
            if sector not in summary:
                summary[sector] = {"total_allocated": 0, "total_spent": 0, "total_remaining": 0}

            summary[sector]["total_allocated"] += record.get("Allocated_Budget", 0)
            summary[sector]["total_spent"] += record.get("Spent_Amount", 0)
            summary[sector]["total_remaining"] += record.get("Remaining_Budget", 0)

    if not summary:
        raise HTTPException(status_code=404, detail=f"No budget data found for subsidiary: {subsidiary}")

    return [{"Sector": sec, **vals} for sec, vals in summary.items()]


# 3️⃣ **Fetch budget by sector (Admin & Viewer)**
@app.get("/budget/sector/{sector}")
def get_budget_by_sector(sector: str, user_role: dict = Depends(lambda: get_user_role("viewer"))):
    ref = db.reference("/budget_transactions")
    transactions = ref.get()

    if not transactions:
        raise HTTPException(status_code=404, detail="No budget data available")

    summary = {}

    for record in transactions:
        if isinstance(record, dict) and record.get("Sector") == sector:
            subsidiary = record.get("Subsidiary", "Unknown")
            if subsidiary not in summary:
                summary[subsidiary] = {"total_allocated": 0, "total_spent": 0, "total_remaining": 0}

            summary[subsidiary]["total_allocated"] += record.get("Allocated_Budget", 0)
            summary[subsidiary]["total_spent"] += record.get("Spent_Amount", 0)
            summary[subsidiary]["total_remaining"] += record.get("Remaining_Budget", 0)

    if not summary:
        raise HTTPException(status_code=404, detail=f"No budget data found for sector: {sector}")

    return [{"Subsidiary": sub, **vals} for sub, vals in summary.items()]


# 4️⃣ **Fetch all transactions (Admin & Viewer)**
@app.get("/transactions")
def get_all_transactions(user_role: dict = Depends(lambda: get_user_role("viewer"))):
    ref = db.reference("/budget_transactions")
    transactions = ref.get()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    return transactions  # No need to use `.items()`, return list directly


# 5️⃣ **Add a new transaction (Admin Only)**
@app.post("/transactions/add")
def add_transaction(
        Transaction_ID: str,
        Date: str,
        Subsidiary: str,
        Sector: str,
        User_ID: str,
        Allocated_Budget: float,
        Spent_Amount: float,
        Remaining_Budget: float,
        Revenue_Generated: float,
        Transaction_Type: str,
        user_role: dict = Depends(lambda: get_user_role("admin"))
):
    if not user_role["can_edit"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    ref = db.reference("/budget_transactions")
    transactions = ref.get() or []  # Get existing transactions or an empty list
    new_transaction = {
        "Transaction_ID": Transaction_ID,
        "Date": Date,
        "Subsidiary": Subsidiary,
        "Sector": Sector,
        "User_ID": User_ID,
        "Allocated_Budget": Allocated_Budget,
        "Spent_Amount": Spent_Amount,
        "Remaining_Budget": Remaining_Budget,
        "Revenue_Generated": Revenue_Generated,
        "Transaction_Type": Transaction_Type
    }

    transactions.append(new_transaction)
    ref.set(transactions)  # Save updated list back to Firebase

    return {"message": "Transaction added successfully"}


# 6️⃣ **Delete a transaction (Admin Only)**
@app.delete("/transactions/delete/{transaction_id}")
def delete_transaction(transaction_id: str, user_role: dict = Depends(lambda: get_user_role("admin"))):
    if not user_role["can_edit"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    ref = db.reference("/budget_transactions")
    transactions = ref.get()

    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    # Filter out the transaction with the given ID
    updated_transactions = [t for t in transactions if t.get("Transaction_ID") != transaction_id]

    if len(updated_transactions) == len(transactions):
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    ref.set(updated_transactions)  # Save updated list to Firebase

    return {"message": f"Transaction {transaction_id} deleted successfully"}


'''from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import create_engine, text
from typing import Literal

app = FastAPI()

# Database Connection
#DATABASE_URL = "mysql+pymysql://root:pranjal@localhost:3306/budget_db"
DATABASE_URL = "mysql+pymysql://if0_38623850:SDci3xl8GCsWt@sql210.infinityfree.com/if0_38623850_budget_db"
engine = create_engine(DATABASE_URL)

# Mock User Roles (Replace with actual authentication in a real system)
USER_ROLES = {
    "admin": {"can_edit": True, "can_view": True},
    "viewer": {"can_edit": False, "can_view": True}
}

def get_user_role(role: Literal["admin", "viewer"]):
    """Checks if the user role is valid and returns role permissions."""
    if role not in USER_ROLES:
        raise HTTPException(status_code=403, detail="Invalid user role")
    return USER_ROLES[role]

@app.get("/")
def home():
    return {"message": "Welcome to the Budget Dashboard API"}

# 1️⃣ **Fetch total budget summary (Admin & Viewer)**
@app.get("/budget/summary")
def get_budget_summary(user_role: dict = Depends(lambda: get_user_role("viewer"))):
    query = """
    SELECT 
        Subsidiary,
        Sector,
        SUM(Allocated_Budget) AS total_allocated,
        SUM(Spent_Amount) AS total_spent,
        SUM(Remaining_Budget) AS total_remaining
    FROM budget_transactions
    GROUP BY Subsidiary, Sector;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query)).mappings().all()
    if not result:
        raise HTTPException(status_code=404, detail="No budget data available")
    return result

# 2️⃣ **Fetch budget by subsidiary (Admin & Viewer)**
@app.get("/budget/subsidiary/{subsidiary}")
def get_budget_by_subsidiary(subsidiary: str, user_role: dict = Depends(lambda: get_user_role("viewer"))):
    query = """
    SELECT 
        Sector,
        SUM(Allocated_Budget) AS total_allocated,
        SUM(Spent_Amount) AS total_spent,
        SUM(Remaining_Budget) AS total_remaining
    FROM budget_transactions
    WHERE Subsidiary = :subsidiary
    GROUP BY Sector;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"subsidiary": subsidiary}).mappings().all()
    if not result:
        raise HTTPException(status_code=404, detail=f"No budget data found for subsidiary: {subsidiary}")
    return result

# 3️⃣ **Fetch budget by sector (Admin & Viewer)**
@app.get("/budget/sector/{sector}")
def get_budget_by_sector(sector: str, user_role: dict = Depends(lambda: get_user_role("viewer"))):
    query = """
    SELECT 
        Subsidiary,
        SUM(Allocated_Budget) AS total_allocated,
        SUM(Spent_Amount) AS total_spent,
        SUM(Remaining_Budget) AS total_remaining
    FROM budget_transactions
    WHERE Sector = :sector
    GROUP BY Subsidiary;
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), {"sector": sector}).mappings().all()
    if not result:
        raise HTTPException(status_code=404, detail=f"No budget data found for sector: {sector}")
    return result

# 4️⃣ **Fetch all transactions (Admin & Viewer)**
@app.get("/transactions")
def get_all_transactions(user_role: dict = Depends(lambda: get_user_role("viewer"))):
    query = "SELECT * FROM budget_transactions"
    with engine.connect() as conn:
        transactions = conn.execute(text(query)).mappings().all()
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")
    return transactions

# 5️⃣ **Add a new transaction (Admin Only)**
@app.post("/transactions/add")
def add_transaction(
    Transaction_ID: str,
    Date: str,
    Subsidiary: str,
    Sector: str,
    User_ID: str,
    Allocated_Budget: float,
    Spent_Amount: float,
    Remaining_Budget: float,
    Revenue_Generated: float,
    Transaction_Type: str,
    user_role: dict = Depends(lambda: get_user_role("admin"))  # Only Admin can edit
):
    if not user_role["can_edit"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    query = text("""
        INSERT INTO budget_transactions (Transaction_ID, Date, Subsidiary, Sector, User_ID, 
        Allocated_Budget, Spent_Amount, Remaining_Budget, Revenue_Generated, Transaction_Type)
        VALUES (:Transaction_ID, :Date, :Subsidiary, :Sector, :User_ID, 
        :Allocated_Budget, :Spent_Amount, :Remaining_Budget, :Revenue_Generated, :Transaction_Type)
    """)
    with engine.connect() as conn:
        conn.execute(query, {
            "Transaction_ID": Transaction_ID,
            "Date": Date,
            "Subsidiary": Subsidiary,
            "Sector": Sector,
            "User_ID": User_ID,
            "Allocated_Budget": Allocated_Budget,
            "Spent_Amount": Spent_Amount,
            "Remaining_Budget": Remaining_Budget,
            "Revenue_Generated": Revenue_Generated,
            "Transaction_Type": Transaction_Type
        })
        conn.commit()
    return {"message": "Transaction added successfully"}


# 6️⃣ **Update an existing transaction (Admin Only)**
@app.put("/transactions/update/{transaction_id}")
def update_transaction(
    transaction_id: str,
    Date: str = None,
    Subsidiary: str = None,
    Sector: str = None,
    User_ID: str = None,
    Allocated_Budget: float = None,
    Spent_Amount: float = None,
    Remaining_Budget: float = None,
    Revenue_Generated: float = None,
    Transaction_Type: str = None,
    user_role: dict = Depends(lambda: get_user_role("admin"))  # Only Admin can edit
):
    if not user_role["can_edit"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    # Dynamically generate update query
    fields = {
        "Date": Date,
        "Subsidiary": Subsidiary,
        "Sector": Sector,
        "User_ID": User_ID,
        "Allocated_Budget": Allocated_Budget,
        "Spent_Amount": Spent_Amount,
        "Remaining_Budget": Remaining_Budget,
        "Revenue_Generated": Revenue_Generated,
        "Transaction_Type": Transaction_Type
    }

    update_fields = ", ".join([f"{key} = :{key}" for key, value in fields.items() if value is not None])
    if not update_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    query = text(f"""
        UPDATE budget_transactions 
        SET {update_fields}
        WHERE Transaction_ID = :transaction_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {"transaction_id": transaction_id, **{k: v for k, v in fields.items() if v is not None}})
        conn.commit()

    return {"message": f"Transaction {transaction_id} updated successfully"}

# 7️⃣ **Delete a transaction (Admin Only)**
@app.delete("/transactions/delete/{transaction_id}")
def delete_transaction(transaction_id: str, user_role: dict = Depends(lambda: get_user_role("admin"))):
    if not user_role["can_edit"]:
        raise HTTPException(status_code=403, detail="Permission denied")

    query = text("DELETE FROM budget_transactions WHERE Transaction_ID = :transaction_id")

    with engine.connect() as conn:
        result = conn.execute(query, {"transaction_id": transaction_id})
        conn.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail=f"Transaction {transaction_id} not found")

    return {"message": f"Transaction {transaction_id} deleted successfully"}
'''