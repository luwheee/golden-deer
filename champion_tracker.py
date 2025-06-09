import streamlit as st
import pandas as pd
import copy
import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# --- Config ---
SPREADSHEET_ID = "YOUR_GOOGLE_SHEET_ID"  # Replace with your sheet ID from URL
SHEET_NAME = "Scores"
CREDS_FILE = "champion_tracker_creds.json"

agents = [
    "Louie Bartolome", "Riley Peñaflorida", "Dominick Xavier Alonso Bandin",
    "Jesica Anna Mikaela Latar", "Jona Alcazaren", "Luis De Guzman",
    "Maribelle Rosal", "Nicole Daep", "Sofiah Morcilla", "Winston Pasia"
]

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

# --- Google Sheets API setup ---
@st.cache_resource
def get_sheets_service():
    creds = Credentials.from_service_account_file(CREDS_FILE, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    service = build('sheets', 'v4', credentials=creds)
    return service.spreadsheets()

def load_scores_from_sheet():
    sheet = get_sheets_service()
    result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=f"{SHEET_NAME}!A2:C").execute()
    values = result.get('values', [])

    # Initialize dicts with zeroes
    prospecting = {agent: 0 for agent in agents}
    recruitment = {agent: 0 for agent in agents}

    for row in values:
        # row = [Agent, Prospecting, Recruitment]
        agent = row[0]
        if agent in agents:
            prospecting[agent] = int(row[1]) if len(row) > 1 and row[1].isdigit() else 0
            recruitment[agent] = int(row[2]) if len(row) > 2 and row[2].isdigit() else 0
    return prospecting, recruitment

def save_scores_to_sheet(prospecting, recruitment):
    sheet = get_sheets_service()
    data = []
    for agent in agents:
        data.append([agent, prospecting[agent], recruitment[agent]])
    body = {
        'values': data
    }
    sheet.values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{SHEET_NAME}!A2:C",
        valueInputOption="USER_ENTERED",
        body=body
    ).execute()

# --- Undo/Redo stack helpers ---
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
        save_scores_to_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)

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
        save_scores_to_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)

# --- Main app ---
st.title("🔰 Skyline Summit Unit Champion Tracker 🔰")

if "prospecting_scores" not in st.session_state:
    prospecting, recruitment = load_scores_from_sheet()
    st.session_state.prospecting_scores = prospecting
    st.session_state.recruitment_scores = recruitment
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []
if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = []

tab1, tab2 = st.tabs(["🧲 Prospecting Champion", "💼 Recruitment Champion"])

# Prospecting Tab
with tab1:
    st.subheader("Update Prospecting Points")
    selected_agents = st.multiselect("Select agents", agents)
    with st.form("pros_form"):
        counts = {label: st.number_input(f"{label} (+{pts})", min_value=0, step=1) for label, pts in prospecting_points.items()}
        submitted = st.form_submit_button("Submit")
    if submitted:
        if selected_agents:
            push_undo()
            for agent in selected_agents:
                for activity, count in counts.items():
                    st.session_state.prospecting_scores[agent] += prospecting_points[activity] * count
            save_scores_to_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
            st.success("Points updated.")

    c1, c2, c3 = st.columns(3)
    if c1.button("Undo"):
        undo()
    if c2.button("Redo"):
        redo()
    if c3.button("Clear All"):
        push_undo()
        st.session_state.prospecting_scores = {agent: 0 for agent in agents}
        save_scores_to_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
        st.success("Scores cleared.")

    df_pro = pd.DataFrame(st.session_state.prospecting_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_pro)
    st.bar_chart(df_pro.set_index("Agent"))

# Recruitment Tab
with tab2:
    st.subheader("Update Recruitment Points")
    selected_agents = st.multiselect("Select agents", agents, key="recruitment")
    with st.form("rec_form"):
        counts = {label: st.number_input(f"{label} (+{pts})", min_value=0, step=1, key=label) for label, pts in recruitment_points.items()}
        submitted = st.form_submit_button("Submit")
    if submitted:
        if selected_agents:
            push_undo()
            for agent in selected_agents:
                for activity, count in counts.items():
                    st.session_state.recruitment_scores[agent] += recruitment_points[activity] * count
            save_scores_to_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
            st.success("Points updated.")

    c1, c2, c3 = st.columns(3)
    if c1.button("Undo", key="undo2"):
        undo()
    if c2.button("Redo", key="redo2"):
        redo()
    if c3.button("Clear All", key="clear2"):
        push_undo()
        st.session_state.recruitment_scores = {agent: 0 for agent in agents}
        save_scores_to_sheet(st.session_state.prospecting_scores, st.session_state.recruitment_scores)
        st.success("Scores cleared.")

    df_rec = pd.DataFrame(st.session_state.recruitment_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_rec)
    st.bar_chart(df_rec.set_index("Agent"))
