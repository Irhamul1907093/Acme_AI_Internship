import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# Load Firebase credentials
cred = credentials.Certificate("firebase-adminsdk.json")
firebase_admin.initialize_app(cred, {'databaseURL': 'https://budgetdb-7d811-default-rtdb.firebaseio.com/'})

# Fetch data
def fetch_budget_data():
    ref = db.reference("/budget_transactions")
    data = ref.get()
    if data:
        return pd.DataFrame(data)  # Convert to DataFrame
    return pd.DataFrame()

# Example usage
if __name__ == "__main__":
    df = fetch_budget_data()
    print(df.head())
