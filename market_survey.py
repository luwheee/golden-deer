import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="Budget Tracker", layout="centered")

# --- Authentication ---
scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(
    st.secrets["google_service_account"], scopes=scope
)
gc = gspread.authorize(credentials)

# --- Sheet Setup ---
SHEET_KEY = "19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI"
MAIN_SHEET_ID = 1016758700

try:
    sheet = gc.open_by_key(SHEET_KEY)
    worksheet = sheet.get_worksheet_by_id(MAIN_SHEET_ID)
    undo_sheet = None
    try:
        undo_sheet = sheet.worksheet("UndoRedo")
    except:
        undo_sheet = sheet.add_worksheet(title="UndoRedo", rows="100", cols="10")
        undo_sheet.append_row(["Date", "Type", "Category", "Amount", "Action"])  # Action: undo/redo
except Exception as e:
    st.error(f"Google Sheet error: {e}")
    st.stop()

# --- Categories ---
income_categories = ["Salary", "Business", "Investment", "Gift", "Other"]
expense_categories = ["Food", "Transportation", "Bills", "Shopping", "Emergency Fund", "Savings", "Extra Money", "Other"]

# --- UI Title ---
st.title("💸 Budget Tracker")

# --- Entry Input ---
st.sidebar.header("Add New Entry")
entry_type = st.sidebar.selectbox("Type", ["Income", "Expense"])
category = st.sidebar.selectbox("Category", income_categories if entry_type == "Income" else expense_categories)
amount = st.sidebar.number_input("Amount", min_value=0.0, step=0.01, format="%.2f")
date = st.sidebar.date_input("Date", datetime.today())

if st.sidebar.button("Submit"):
    if amount > 0:
        row = [date.strftime("%Y-%m-%d"), entry_type, category, f"{amount:.2f}"]
        worksheet.append_row(row)
        undo_sheet.append_row(row + ["undo"])
        st.sidebar.success("Entry added!")
    else:
        st.sidebar.error("Amount must be greater than 0.")

# --- Load Main Data ---
try:
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except Exception as e:
    st.error(f"Data load failed: {e}")
    st.stop()

# --- Data Validation ---
required = ["Date", "Type", "Category", "Amount"]
if any(col not in df.columns for col in required):
    st.error("Missing required columns in your sheet.")
    st.stop()

df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce").fillna(0)
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

# --- Summary ---
st.subheader("📊 Summary")
total_income = df[df["Type"] == "Income"]["Amount"].sum()
total_expense = df[df["Type"] == "Expense"]["Amount"].sum()
balance = total_income - total_expense

st.metric("Total Income", f"₱{total_income:,.2f}")
st.metric("Total Expense", f"₱{total_expense:,.2f}")
st.metric("Net Balance", f"₱{balance:,.2f}")

# --- Category Breakdown ---
st.markdown("### 📂 Category Breakdown")
cat_summary = df.groupby(["Type", "Category"])["Amount"].sum().reset_index()

for t in ["Income", "Expense"]:
    cat_df = cat_summary[cat_summary["Type"] == t]
    if not cat_df.empty:
        st.markdown(f"**{t} Categories**")
        for _, row in cat_df.iterrows():
            st.write(f"➡️ {row['Category']}: ₱{row['Amount']:,.2f}")

# --- Transactions ---
st.markdown("### 📅 Transactions")
st.dataframe(df.sort_values("Date", ascending=False))

# --- Undo/Redo/Reset Logic ---
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("↩️ Undo Last Entry"):
        undo_data = undo_sheet.get_all_records()
        if undo_data:
            last = undo_data[-1]
            if last["Action"] == "undo":
                values = [last["Date"], last["Type"], last["Category"], last["Amount"]]
                records = worksheet.get_all_values()
                if records and values in records:
                    idx = records.index(values) + 1
                    worksheet.delete_rows(idx)
                    undo_sheet.append_row(values + ["redo"])
                    st.success("Last entry undone.")
                else:
                    st.warning("No matching entry to undo.")

with col2:
    if st.button("↪️ Redo Last Undo"):
        undo_data = undo_sheet.get_all_records()
        for last in reversed(undo_data):
            if last["Action"] == "redo":
                values = [last["Date"], last["Type"], last["Category"], last["Amount"]]
                worksheet.append_row(values)
                undo_sheet.append_row(values + ["undo"])
                st.success("Redo successful.")
                break
        else:
            st.warning("Nothing to redo.")

with col3:
    if st.button("🗑️ Reset All Data"):
        confirm = st.checkbox("I understand this will delete everything.", key="confirm_reset")
        if confirm:
            records = worksheet.get_all_values()
            for i in range(len(records), 1, -1):  # Skip header
                worksheet.delete_rows(i)
            st.success("All data reset!")

