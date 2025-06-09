import json
import streamlit as st
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# --- Load Google Sheets credentials from Streamlit secrets ---
def get_sheets_service():
    try:
        service_account_info = json.loads(st.secrets["google_service_account"]["json"])
        creds = Credentials.from_service_account_info(
            service_account_info,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        service = build('sheets', 'v4', credentials=creds)
        return service.spreadsheets()
    except Exception as e:
        st.error("❌ Failed to authenticate with Google Sheets.")
        st.exception(e)
        return None

# --- Load data from Google Sheets ---
def load_scores_from_sheet():
    sheet = get_sheets_service()
    if sheet is None:
        return [], [], []

    SPREADSHEET_ID = "19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI"
    RANGE_NAME = "Scores!A1:C11"

    try:
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE_NAME).execute()
        values = result.get('values', [])

        agents, prospecting_scores, recruitment_scores = [], [], []

        for row in values[1:]:  # Skip header
            agents.append(row[0] if len(row) > 0 else "")
            prospecting_scores.append(int(row[1]) if len(row) > 1 and row[1].isdigit() else 0)
            recruitment_scores.append(int(row[2]) if len(row) > 2 and row[2].isdigit() else 0)

        return agents, prospecting_scores, recruitment_scores

    except HttpError as e:
        st.error("❌ Failed to load data. Please check your spreadsheet ID and range name.")
        st.exception(e)
        return [], [], []

# --- Streamlit UI ---
def main():
    st.set_page_config(page_title="Champion Tracker", layout="centered")
    st.title("🏆 Champion Tracker")

    agents, prospecting, recruitment = load_scores_from_sheet()

    if agents:
        st.subheader("Agent Scores")
        for i, agent in enumerate(agents):
            st.markdown(f"""
                **{agent}**
                - 🔍 Prospecting: `{prospecting[i]}`
                - 👥 Recruitment: `{recruitment[i]}`
            """)
    else:
        st.warning("⚠️ No data available.")

if __name__ == "__main__":
    main()
