import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Budget Tracker", layout="centered")

# Authenticate with Google Sheets
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(
    st.secrets["google_service_account"], scopes=scope
)
gc = gspread.authorize(credentials)

# Open spreadsheet and worksheet
try:
    sheet = gc.open_by_key("19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI")
    worksheet = sheet.get_worksheet_by_id(1016758700)
except Exception as e:
    st.error(f"Error opening Google Sheet: {e}")
    st.stop()

# --- App Title ---
st.title("💸 Budget Tracker")

# --- Sidebar Input ---
st.sidebar.header("Add New Entry")
entry_type = st.sidebar.selectbox("Type", ["Income", "Expense"])
category = st.sidebar.selectbox("Category", [
    "Salary", "Business", "Gift", "Other (Income)",
    "Food", "Transportation", "Utilities", "Savings", "Emergency Fund", "Extra Money", "Other (Expense)"
])
amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Submit"):
    if amount > 0:
        try:
            worksheet.append_row([
                date.strftime("%Y-%m-%d"),
                entry_type,
                category,
                f"{amount:.2f}"
            ])
            st.sidebar.success("Entry added successfully!")
        except Exception as e:
            st.sidebar.error(f"Failed to add entry: {e}")
    else:
        st.sidebar.error("Amount must be greater than 0.")

# --- Load Data ---
try:
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

if not df.empty:
    df["Amount"] = pd.to_numeric(df.get("Amount", 0), errors="coerce").fillna(0)
    df["Date"] = pd.to_datetime(df.get("Date", datetime.today()), errors="coerce")

    # Summary
    st.subheader("📊 Summary")
    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.metric("Total Income", f"₱{total_income:,.2f}")
    st.metric("Total Expense", f"₱{total_expense:,.2f}")
    st.metric("Net Balance", f"₱{balance:,.2f}")

    # Category Breakdown
    st.subheader("Category Breakdown")
    category_summary = df.groupby(["Type", "Category"])["Amount"].sum().reset_index()
    st.dataframe(category_summary)

    # Transactions Table
    st.subheader("📅 Transactions")
    st.dataframe(df.sort_values("Date", ascending=False))
else:
    st.info("No data yet. Use the sidebar to add entries.")

# --- Reset Section ---
st.subheader("🚳 Reset Data")
with st.expander("Danger Zone - Reset All Data"):
    confirm = st.checkbox("Yes, I understand this will delete all entries.")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✔️ Confirm Reset"):
            if confirm:
                worksheet.batch_clear(['A2:D'])
                st.success("All data has been reset.")
            else:
                st.warning("Please check the confirmation box before resetting.")
    with col2:
        if st.button("❌ Cancel Reset"):
            st.info("Reset cancelled.")
