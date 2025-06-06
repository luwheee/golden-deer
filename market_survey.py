import streamlit as st
import pandas as pd

# Title
st.title("💰 Budget Tracker")

# Initialize session state for storing data
if "budget_data" not in st.session_state:
    st.session_state.budget_data = []

# User input form
with st.form("budget_form"):
    date = st.date_input("Transaction Date")
    transaction_type = st.selectbox("Transaction Type", ["Income", "Expense"])
    category = st.selectbox("Category", ["Salary", "Rent", "Food", "Transportation", "Entertainment", "Savings", "Other"])
    description = st.text_input("Description")
    amount = st.number_input("Amount", min_value=0.0, format="%.2f")
    submitted = st.form_submit_button("Add Transaction")

# Storing data
if submitted:
    entry = {
        "Date": date,
        "Transaction Type": transaction_type,
        "Category": category,
        "Description": description,
        "Amount": amount * (1 if transaction_type == "Income" else -1),  # Negative for expenses
    }
    st.session_state.budget_data.append(entry)

# Display stored data with edit options
if st.session_state.budget_data:
    df = pd.DataFrame(st.session_state.budget_data)
    st.write("### Budget Transactions")

    edited_df = st.data_editor(df, num_rows="dynamic")  # Editable table

    # Save the edited dataframe back to session state
    if st.button("Save Changes"):
        st.session_state.budget_data = edited_df.to_dict("records")
        st.success("Updates saved successfully!")

    # Calculate total income, expenses, and balance
    total_income = df[df["Transaction Type"] == "Income"]["Amount"].sum()
    total_expense = abs(df[df["Transaction Type"] == "Expense"]["Amount"].sum())
    net_balance = total_income - total_expense

    # Display financial summary
    st.write("### Financial Summary")
    st.metric("Total Income", f"₱{total_income:,.2f}")
    st.metric("Total Expenses", f"₱{total_expense:,.2f}")
    st.metric("Net Balance", f"₱{net_balance:,.2f}")

    # Visualizing Inflow and Outflow with a Bar Chart
    category_totals = df.groupby(["Transaction Type", "Category"])["Amount"].sum().reset_index()
    st.write("### Income & Expense Breakdown")
    st.bar_chart(category_totals, x="Category", y="Amount", color="Transaction Type")

    # Export data option
    csv = df.to_csv(index=False)
    st.download_button("Download Data as CSV", csv, "budget_data.csv", "text/csv")