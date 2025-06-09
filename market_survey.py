import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

# Set page config
st.set_page_config(page_title="Budget Tracker", layout="centered")

# Authenticate with Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    st.secrets["google_service_account"], scopes=scope
)
gc = gspread.authorize(credentials)
sheet = gc.open("Skyline Summit Tracker")
worksheet = sheet.sheet1

# --- App Title ---
st.title("💸 Budget Tracker")

# --- Sidebar for Entry ---
st.sidebar.header("Add New Entry")
entry_type = st.sidebar.selectbox("Type", ["Income", "Expense"])
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01)
date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Submit"):
    if description and amount > 0:
        worksheet.append_row([
            date.strftime("%Y-%m-%d"),
            entry_type,
            description,
            amount
        ])
        st.sidebar.success("Entry added successfully!")
    else:
        st.sidebar.error("Please provide all required fields.")

# --- Load and Display Data ---
data = worksheet.get_all_records()
df = pd.DataFrame(data)

if not df.empty:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    df["Date"] = pd.to_datetime(df["Date"])

    st.subheader("📊 Summary")
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.metric("Total Income", f"₱{total_income:,.2f}")
    st.metric("Total Expense", f"₱{total_expense:,.2f}")
    st.metric("Balance", f"₱{balance:,.2f}")

    st.subheader("📅 Transactions")
    st.dataframe(df.sort_values("Date", ascending=False))
else:
    st.info("No data yet. Use the sidebar to add entries.")
