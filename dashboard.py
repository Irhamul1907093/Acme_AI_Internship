import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Backend API URL
BASE_URL = "https://acme-budget-api.onrender.com/"

# Set page configuration
st.set_page_config(page_title="Budget Dashboard", layout="wide")

st.title("📊 Budget Dashboard")

# 🔹 Select User Role (Admin or Viewer)
role = st.sidebar.radio("Select User Role:", ["viewer", "admin"])
st.sidebar.write(f"🛡️ **Current Role: {role.capitalize()}**")

# Role-based access control
is_admin = role == "admin"

# Subsidiary & Sector Options
SUBSIDIARY_OPTIONS = ["Branch A", "Branch B", "Branch C"]
SECTOR_OPTIONS = ["R&D", "Marketing", "HR", "Operations", "IT"]

# Fetch Budget Summary
st.subheader("Total Budget Overview")
response = requests.get(f"{BASE_URL}/budget/summary")
if response.status_code == 200:
    budget_data = pd.DataFrame(response.json())
    st.dataframe(budget_data)
else:
    st.error("Failed to load budget summary!")



# Filter by Subsidiary
selected_subsidiary = st.selectbox("🔍 Filter by Subsidiary", ["All"] + SUBSIDIARY_OPTIONS)
if selected_subsidiary != "All":
    sub_response = requests.get(f"{BASE_URL}/budget/subsidiary/{selected_subsidiary}")
    if sub_response.status_code == 200:
        st.write("### Subsidiary Budget Breakdown")
        st.dataframe(pd.DataFrame(sub_response.json()))
    else:
        st.error("Subsidiary not found!")

# Filter by Sector
selected_sector = st.selectbox("🔍 Filter by Sector", ["All"] + SECTOR_OPTIONS)
if selected_sector != "All":
    sec_response = requests.get(f"{BASE_URL}/budget/sector/{selected_sector}")
    if sec_response.status_code == 200:
        st.write("### Sector Budget Breakdown")
        st.dataframe(pd.DataFrame(sec_response.json()))
    else:
        st.error("Sector not found!")

# Fetch All Transactions
st.subheader("💰 Transaction History")
trans_response = requests.get(f"{BASE_URL}/transactions")
if trans_response.status_code == 200:
    transactions = pd.DataFrame(trans_response.json())
    st.dataframe(transactions)
else:
    st.error("Failed to load transactions!")

# 🔹 ADMIN FUNCTIONALITY
if is_admin:
    st.subheader("⚡ Admin Actions: Manage Transactions")

    # Add a New Transaction
    st.markdown("### ➕ Add a Transaction")
    with st.form("add_transaction_form"):
        Transaction_ID = st.text_input("Transaction ID")
        Date = st.date_input("Date")
        Subsidiary = st.selectbox("Subsidiary", SUBSIDIARY_OPTIONS)  # 🔹 Dropdown added
        Sector = st.selectbox("Sector", SECTOR_OPTIONS)  # 🔹 Dropdown added
        User_ID = st.text_input("User ID")
        Allocated_Budget = st.number_input("Allocated Budget", min_value=0.0, step=100.0)
        Spent_Amount = st.number_input("Spent Amount", min_value=0.0, step=100.0)
        Remaining_Budget = Allocated_Budget - Spent_Amount
        Revenue_Generated = st.number_input("Revenue Generated", min_value=0.0, step=100.0)
        Transaction_Type = st.selectbox("Transaction Type", ["Credit", "Debit"])
        submit_button = st.form_submit_button("Add Transaction")

        if submit_button:
            payload = {
                "Transaction_ID": Transaction_ID,
                "Date": str(Date),
                "Subsidiary": Subsidiary,
                "Sector": Sector,
                "User_ID": User_ID,
                "Allocated_Budget": Allocated_Budget,
                "Spent_Amount": Spent_Amount,
                "Remaining_Budget": Remaining_Budget,
                "Revenue_Generated": Revenue_Generated,
                "Transaction_Type": Transaction_Type
            }
            response = requests.post(f"{BASE_URL}/transactions/add", params=payload)
            if response.status_code == 200:
                st.success("Transaction added successfully!")
            else:
                st.error(response.json()["detail"])

    # Update an Existing Transaction
    st.markdown("### ✏️ Update a Transaction")
    with st.form("update_transaction_form"):
        update_transaction_id = st.text_input("Transaction ID to Update")
        updated_fields = {}

        if st.checkbox("Update Date"):
            updated_fields["Date"] = str(st.date_input("New Date"))
        if st.checkbox("Update Subsidiary"):
            updated_fields["Subsidiary"] = st.selectbox("New Subsidiary", SUBSIDIARY_OPTIONS)
        if st.checkbox("Update Sector"):
            updated_fields["Sector"] = st.selectbox("New Sector", SECTOR_OPTIONS)
        if st.checkbox("Update Allocated Budget"):
            updated_fields["Allocated_Budget"] = st.number_input("New Allocated Budget", min_value=0.0, step=100.0)
        if st.checkbox("Update Spent Amount"):
            updated_fields["Spent_Amount"] = st.number_input("New Spent Amount", min_value=0.0, step=100.0)
        if st.checkbox("Update Revenue Generated"):
            updated_fields["Revenue_Generated"] = st.number_input("New Revenue Generated", min_value=0.0, step=100.0)
        if st.checkbox("Update Transaction Type"):
            updated_fields["Transaction_Type"] = st.selectbox("New Transaction Type", ["Credit", "Debit"])

        update_submit = st.form_submit_button("Update Transaction")

        if update_submit and update_transaction_id:
            response = requests.put(f"{BASE_URL}/transactions/update/{update_transaction_id}", params=updated_fields)
            if response.status_code == 200:
                st.success(f"Transaction {update_transaction_id} updated successfully!")
            else:
                st.error(response.json()["detail"])

    # Delete a Transaction
    st.markdown("### 🗑️ Delete a Transaction")
    delete_transaction_id = st.text_input("Transaction ID to Delete")
    if st.button("Delete Transaction"):
        delete_response = requests.delete(f"{BASE_URL}/transactions/delete/{delete_transaction_id}")
        if delete_response.status_code == 200:
            st.success(f"Transaction {delete_transaction_id} deleted successfully!")
        else:
            st.error(delete_response.json()["detail"])
