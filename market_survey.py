import streamlit as st
import pandas as pd
import json
import gspread
from google.oauth2.service_account import Credentials

# --- Google Sheets setup ---
service_account_info = json.loads(st.secrets["google_service_account"]["json"])
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file"]
credentials = Credentials.from_service_account_info(service_account_info, scopes=scope)
gc = gspread.authorize(credentials)

GOOGLE_SHEET_ID = "19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI"
GOOGLE_SHEET_NAME = "Sheet1"
sheet = gc.open_by_key(GOOGLE_SHEET_ID).worksheet(GOOGLE_SHEET_NAME)

# --- Load data from sheet ---
def load_data():
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# --- Save data back to sheet ---
def save_data(df: pd.DataFrame):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# --- Initialize session state for new entries ---
if "budget_data" not in st.session_state:
    st.session_state.budget_data = load_data()

st.title("💰 Budget Tracker with Google Sheets Sync")

# --- Transaction input form ---
with st.form("budget_form"):
    date = st.date_input("Transaction Date")
    transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    category = st.selectbox("Category", ["Salary", "Rent", "Food", "Transportation", "Entertainment", "Savings", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Transaction")

if submitted:
    entry = {
        "Date": date.strftime("%Y-%m-%d"),  # Format for consistency
        "Transaction Type": transaction_type,
        "Category": category,
        "Description": description,
        "Amount": amount if transaction_type == "Income" else -amount,
    }
    st.session_state.budget_data = pd.concat([st.session_state.budget_data, pd.DataFrame([entry])], ignore_index=True)
    save_data(st.session_state.budget_data)
    st.success("Transaction added and synced to Google Sheets!")

# --- Display and edit existing data ---
if not st.session_state.budget_data.empty:
    st.write("### Budget Transactions")
    edited_df = st.data_editor(st.session_state.budget_data, num_rows="dynamic")

    if st.button("Save Changes"):
        st.session_state.budget_data = edited_df
        save_data(edited_df)
        st.success("Changes saved to Google Sheets!")

    # --- Financial Summary ---
    df = st.session_state.budget_data
    total_income = df[df["Transaction Type"] == "Income"]["Amount"].sum()
    total_expense = abs(df[df["Transaction Type"] == "Expense"]["Amount"].sum())
    net_balance = total_income - total_expense

    st.write("### Financial Summary")
    st.metric("Total Income", f"₱{total_income:,.2f}")
    st.metric("Total Expenses", f"₱{total_expense:,.2f}")
    st.metric("Net Balance", f"₱{net_balance:,.2f}")

    # --- Chart ---
    category_totals = df.groupby(["Transaction Type", "Category"])["Amount"].sum().reset_index()
    st.write("### Income & Expense Breakdown")
    st.bar_chart(category_totals, x="Category", y="Amount", color="Transaction Type")

    # --- Download CSV ---
    csv = df.to_csv(index=False)
    st.download_button("Download Data as CSV", csv, "budget_data.csv", "text/csv")
else:
    st.info("No budget data found yet. Add some transactions!")

