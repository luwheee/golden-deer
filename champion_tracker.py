import streamlit as st
import pandas as pd
import copy
import json
from datetime import date
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Google Sheets Setup
SHEET_NAME = "Scores"
SPREADSHEET_ID = "19jTzhtiTTKPH6MF6kxQPf51CZSURjE1sNPEGwIQ05dI"
RANGE = f"{SHEET_NAME}!A2:C19"

# Load Google Sheets credentials from Streamlit secrets
def get_sheets_service():
    service_account_info = json.loads(st.secrets["google_service_account"]["json"])
    creds = Credentials.from_service_account_info(service_account_info)
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

def fetch_scores():
    sheet = get_sheets_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=RANGE).execute()
    values = result.get('values', [])
    agents = []
    prospecting_scores = {}
    recruitment_scores = {}
    for row in values:
        if len(row) >= 3:
            agent = row[0]
            agents.append(agent)
            prospecting_scores[agent] = int(row[1]) if row[1].isdigit() else 0
            recruitment_scores[agent] = int(row[2]) if row[2].isdigit() else 0
    return agents, prospecting_scores, recruitment_scores

def update_sheet(prospecting_scores, recruitment_scores):
    data = []
    for agent in prospecting_scores:
        data.append([agent, prospecting_scores[agent], recruitment_scores.get(agent, 0)])
    body = {
        'values': data
    }
    sheet = get_sheets_service()
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=RANGE,
        valueInputOption="RAW",
        body=body
    ).execute()

# Load Data
agents, pro_scores, rec_scores = fetch_scores()

st.session_state.prospecting_scores = st.session_state.get("prospecting_scores", pro_scores)
st.session_state.recruitment_scores = st.session_state.get("recruitment_scores", rec_scores)

if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []
if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = []

def push_undo():
    snapshot = {
        "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
        "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
    }
    st.session_state.undo_stack.append(snapshot)
    st.session_state.redo_stack.clear()

def undo():
    if st.session_state.undo_stack:
        current = {
            "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
            "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
        }
        st.session_state.redo_stack.append(current)
        snapshot = st.session_state.undo_stack.pop()
        st.session_state.prospecting_scores = snapshot["prospecting"]
        st.session_state.recruitment_scores = snapshot["recruitment"]
        update_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)

def redo():
    if st.session_state.redo_stack:
        current = {
            "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
            "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
        }
        st.session_state.undo_stack.append(current)
        snapshot = st.session_state.redo_stack.pop()
        st.session_state.prospecting_scores = snapshot["prospecting"]
        st.session_state.recruitment_scores = snapshot["recruitment"]
        update_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)

# Points system
prospecting_points = {
    "Valid Prospect": 1,
    "Successful Quotation Proposal": 2,
    "Successful Appointment": 5
}
recruitment_points = {
    "Successful Initial Interview": 1,
    "Attended COP": 2,
    "Successful Final Interview": 5
}
# Logo from Google Drive
st.image("https://drive.google.com/file/d/13aAGZz1lnnre-de8fUUypHeIyi4Zy1uD/view?usp=sharing", width=120)

# Title
st.title("\U0001F530 Skyline Summit Unit Champion Tracker \U0001F530")

# Tabs
tab1, tab2 = st.tabs(["\U0001F9F2 Prospecting Champion", "\U0001F4BC Recruitment Champion"])

# Prospecting
with tab1:
    st.subheader("Update Prospecting Points")
    selected_agents = st.multiselect("Select agents", agents)
    with st.form("pros_form"):
        counts = {label: st.number_input(f"{label} (+{pts})", min_value=0, step=1) for label, pts in prospecting_points.items()}
        submitted = st.form_submit_button("Submit")
    if submitted and selected_agents:
        push_undo()
        for agent in selected_agents:
            for activity, count in counts.items():
                st.session_state.prospecting_scores[agent] += prospecting_points[activity] * count
        update_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
        st.success("Points updated.")

    col1, col2, col3 = st.columns(3)
    if col1.button("Undo"):
        undo()
    if col2.button("Redo"):
        redo()
    if col3.button("Clear All"):
        push_undo()
        st.session_state.prospecting_scores = {agent: 0 for agent in agents}
        update_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
        st.success("Scores cleared.")

    df_pro = pd.DataFrame(st.session_state.prospecting_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_pro)
    st.bar_chart(df_pro.set_index("Agent"))

# Recruitment
with tab2:
    st.subheader("Update Recruitment Points")
    selected_agents = st.multiselect("Select agents", agents, key="recruitment")
    with st.form("rec_form"):
        counts = {label: st.number_input(f"{label} (+{pts})", min_value=0, step=1, key=label) for label, pts in recruitment_points.items()}
        submitted = st.form_submit_button("Submit")
    if submitted and selected_agents:
        push_undo()
        for agent in selected_agents:
            for activity, count in counts.items():
                st.session_state.recruitment_scores[agent] += recruitment_points[activity] * count
        update_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
        st.success("Points updated.")

    col1, col2, col3 = st.columns(3)
    if col1.button("Undo", key="undo2"):
        undo()
    if col2.button("Redo", key="redo2"):
        redo()
    if col3.button("Clear All", key="clear2"):
        push_undo()
        st.session_state.recruitment_scores = {agent: 0 for agent in agents}
        update_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
        st.success("Scores cleared.")

    df_rec = pd.DataFrame(st.session_state.recruitment_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_rec)
    st.bar_chart(df_rec.set_index("Agent"))
