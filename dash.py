import streamlit as st
import requests

API_BASE_URL = "https://acme-budget-api.onrender.com/"

st.title("💰 Budget Dashboard")

# Fetch Budget Summary
st.subheader("Budget Summary")
response = requests.get(f"{API_BASE_URL}/budget/summary")
if response.status_code == 200:
    data = response.json()
    st.table(data)
else:
    st.error("Failed to fetch budget data")

