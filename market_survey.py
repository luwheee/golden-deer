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

# Open the spreadsheet
try:
    sheet = gc.open_by_key("19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI")
    worksheet = sheet.get_worksheet_by_id(1016758700)
except Exception as e:
    st.error(f"Google Sheet error: {e}")
    st.stop()

# Categories
income_categories = ["Salary", "Business", "Investment", "Gift", "Other"]
expense_categories = ["Food", "Transportation", "Bills", "Shopping", "Emergency Fund", "Savings", "Extra Money", "Other"]

# --- App Title ---
st.title("💸 Budget Tracker")

# --- Sidebar for Entry ---
st.sidebar.header("Add New Entry")
entry_type = st.sidebar.selectbox("Type", ["Income", "Expense"])

# Dynamically show categories
category = st.sidebar.selectbox("Category", income_categories if entry_type == "Income" else expense_categories)

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
        st.sidebar.error("Please provide a valid amount.")

# --- Load and Display Data ---
try:
    data = worksheet.get_all_records()
except Exception as e:
    st.error(f"Failed to fetch data: {e}")
    st.stop()

df = pd.DataFrame(data)

if not df.empty:
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

    st.subheader("📊 Summary")

    total_income = df[df["Type"] == "Income"]["Amount"].sum()
    total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
    balance = total_income - total_expense

    st.metric("Total Income", f"₱{total_income:,.2f}")
    st.metric("Total Expense", f"₱{total_expense:,.2f}")
    st.metric("Net Balance", f"₱{balance:,.2f}")

    st.markdown("### 📂 Category Breakdown")
    category_summary = df.groupby(["Type", "Category"])["Amount"].sum().reset_index()

    for t in ["Income", "Expense"]:
        cat_df = category_summary[category_summary["Type"] == t]
        if not cat_df.empty:
            st.markdown(f"**{t} Categories**")
            for _, row in cat_df.iterrows():
                st.write(f"{row['Category']}: ₱{row['Amount']:,.2f}")

    st.markdown("### 📅 Transactions")
    st.dataframe(df.sort_values("Date", ascending=False))

else:
    st.info("No data yet. Use the sidebar to add entries.")
