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

# Open spreadsheet and worksheet safely
try:
    sheet = gc.open_by_key("19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI")
except Exception as e:
    st.error(f"Could not open spreadsheet: {e}")
    st.stop()

worksheet = None
try:
    # Try fetching by worksheet ID
    worksheet = sheet.get_worksheet_by_id(1016758700)
except AttributeError:
    # Fallback: get all worksheets and find by id manually
    for ws in sheet.worksheets():
        if ws.id == 1016758700:
            worksheet = ws
            break

if worksheet is None:
    st.error("Worksheet with specified ID not found.")
    st.stop()

# --- App Title ---
st.title("💸 Budget Tracker")

# --- Sidebar for Entry ---
st.sidebar.header("Add New Entry")
entry_type = st.sidebar.selectbox("Type", ["Income", "Expense"])
description = st.sidebar.text_input("Description")
amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Submit"):
    if description.strip() and amount > 0:
        try:
            worksheet.append_row([
                date.strftime("%Y-%m-%d"),
                entry_type,
                description.strip(),
                f"{amount:.2f}"
            ])
            st.sidebar.success("Entry added successfully!")
        except Exception as e:
            st.sidebar.error(f"Failed to add entry: {e}")
    else:
        st.sidebar.error("Please provide a description and amount > 0.")

# --- Load and Display Data ---
try:
    data = worksheet.get_all_records()
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()

df = pd.DataFrame(data)

if not df.empty:
    # Defensive column checks
    if "Amount" in df.columns:
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    else:
        st.warning("'Amount' column not found.")

    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    else:
        st.warning("'Date' column not found.")

    if "Type" not in df.columns:
        st.warning("'Type' column not found. Income/Expense summary may be inaccurate.")

    # Calculate summary safely
    total_income = df.loc[df.get("Type") == "Income", "Amount"].sum() if "Type" in df.columns else 0
    total_expense = df.loc[df.get("Type") == "Expense", "Amount"].sum() if "Type" in df.columns else 0
    balance = total_income - total_expense

    st.subheader("📊 Summary")
    st.metric("Total Income", f"₱{total_income:,.2f}")
    st.metric("Total Expense", f"₱{total_expense:,.2f}")
    st.metric("Balance", f"₱{balance:,.2f}")

    st.subheader("📅 Transactions")
    st.dataframe(df.sort_values("Date", ascending=False))
else:
    st.info("No data yet. Use the sidebar to add entries.")
