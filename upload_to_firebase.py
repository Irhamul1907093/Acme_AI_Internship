#https://budgetdb-7d811-default-rtdb.firebaseio.com/

import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# Load Firebase credentials
cred = credentials.Certificate("firebase-adminsdk.json")  # Ensure this file is in your project folder
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://budgetdb-7d811-default-rtdb.firebaseio.com/'  # Replace with your actual URL
})

# Read CSV File
csv_file = "dataset_company_budget_allocation_dashboard.csv"  # Ensure this file is in the same folder
df = pd.read_csv(csv_file)

# Convert DataFrame to dictionary
budget_data = df.to_dict(orient="records")

# Push data to Firebase
ref = db.reference("/budget_transactions")  # Firebase path
ref.set(budget_data)

print("✅ Data uploaded successfully to Firebase!")
