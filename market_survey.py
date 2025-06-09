import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import date

st.set_page_config(page_title="💰 Budget Tracker", layout="centered")
st.title("💰 Budget Tracker")

# Google Sheets setup
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_info(
    st.secrets["google_service_account"],
    scopes=scope
)
client = gspread.authorize(credentials)
sheet_name = st.secrets["google_service_account"]["sheet_name"]

try:
    sheet = client.open(sheet_name).sheet1
except gspread.SpreadsheetNotFound:
    st.error("Google Sheet not found. Check your sheet name in secrets.")
    st.stop()

# Initialize session state
if "budget_data" not in st.session_state:
    # Load data from Google Sheet
    rows = sheet.get_all_records()
    st.session_state.budget_data = rows if rows else []

# Transaction input form
with st.form("budget_form"):
    tx_date = st.date_input("Transaction Date", date.today())
    tx_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    category = st.selectbox("Category", ["Salary", "Rent", "Food", "Transportation", "Entertainment", "Savings", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Transaction")

if submitted:
    entry = {
        "Date": str(tx_date),
        "Transaction Type": tx_type,
        "Category": category,
        "Description": description,
        "Amount": amount if tx_type == "Income" else -amount,
    }
    st.session_state.budget_data.append(entry)
    sheet.append_row(list(entry.values()))
    st.success("Transaction added successfully!")

# Display data if available
if st.session_state.budget_data:
    df = pd.DataFrame(st.session_state.budget_data)
    st.write("### Budget Transactions")

    edited_df = st.data_editor(df, num_rows="dynamic")

    if st.button("Save Changes"):
        st.session_state.budget_data = edited_df.to_dict("records")
        sheet.clear()
        sheet.append_row(list(df.columns))
        sheet.append_rows(df.astype(str).values.tolist())
        st.success("Google Sheet and app data updated!")

    # Summary
    income = df[df["Transaction Type"] == "Income"]["Amount"].sum()
    expense = abs(df[df["Transaction Type"] == "Expense"]["Amount"].sum())
    balance = income - expense

    st.write("### Financial Summary")
    st.metric("Total Income", f"₱{income:,.2f}")
    st.metric("Total Expenses", f"₱{expense:,.2f}")
    st.metric("Net Balance", f"₱{balance:,.2f}")

    # Bar chart
    category_totals = df.groupby(["Transaction Type", "Category"])["Amount"].sum().reset_index()
    st.write("### Income & Expense Breakdown")
    st.bar_chart(category_totals, x="Category", y="Amount", color="Transaction Type")

    # CSV export
    csv = df.to_csv(index=False)
    st.download_button("Download Data as CSV", csv, "budget_data.csv", "text/csv")

# Optional background styling
st.markdown("""
    <style>
    body {
        background-color: #f0f8ff;
    }
    </style>
""", unsafe_allow_html=True)
