import streamlit as st
import requests
import pandas as pd

# Backend API URL
BASE_URL = "http://127.0.0.1:8000"

# Page Title
st.set_page_config(page_title="Budget Dashboard", layout="wide")

st.title("📊 Budget Dashboard")

# Fetch Budget Summary
st.subheader("Total Budget Overview")
response = requests.get(f"{BASE_URL}/budget/summary")
if response.status_code == 200:
    budget_data = pd.DataFrame(response.json())
    st.dataframe(budget_data)
else:
    st.error("Failed to load budget summary!")

# Filter by Subsidiary
subsidiary = st.text_input("🔍 Search by Subsidiary")
if subsidiary:
    sub_response = requests.get(f"{BASE_URL}/budget/subsidiary/{subsidiary}")
    if sub_response.status_code == 200:
        st.write("### Subsidiary Budget Breakdown")
        st.dataframe(pd.DataFrame(sub_response.json()))
    else:
        st.error("Subsidiary not found!")

# Filter by Sector
sector = st.text_input("🔍 Search by Sector")
if sector:
    sec_response = requests.get(f"{BASE_URL}/budget/sector/{sector}")
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

