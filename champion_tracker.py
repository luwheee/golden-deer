import streamlit as st
import pandas as pd
import copy
import json
import os
import gspread
from datetime import date
from oauth2client.service_account import ServiceAccountCredentials

# 🧠 AGENTS
agents = [
    "Louie Bartolome", "Riley Peñaflorida", "Dominick Xavier Alonso Bandin",
    "Jesica Anna Mikaela Latar", "Jona Alcazaren", "Luis De Guzman",
    "Maribelle Rosal", "Nicole Daep", "Sofiah Morcilla", "Winston Pasia"
]

# 🧮 POINT SYSTEMS
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

# 📁 FILE PATH
SAVE_FILE = "scores_data.json"

# 📊 GOOGLE SHEETS FUNCTIONS
def get_gsheet():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("champion_tracker_creds.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open("Skyline Summit Scores").sheet1
    return sheet

def save_to_gsheet():
    sheet = get_gsheet()
    sheet.clear()
    sheet.update("A1", [["Agent", "Prospecting Points", "Recruitment Points"]])
    for agent in agents:
        sheet.append_row([
            agent,
            st.session_state.prospecting_scores.get(agent, 0),
            st.session_state.recruitment_scores.get(agent, 0)
        ])

# 💾 SAVE / LOAD FUNCTIONS
def save_scores():
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "prospecting": st.session_state.prospecting_scores,
            "recruitment": st.session_state.recruitment_scores
        }, f)

def load_scores():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
            st.session_state.prospecting_scores = data.get("prospecting", {agent: 0 for agent in agents})
            st.session_state.recruitment_scores = data.get("recruitment", {agent: 0 for agent in agents})
    else:
        st.session_state.prospecting_scores = {agent: 0 for agent in agents}
        st.session_state.recruitment_scores = {agent: 0 for agent in agents}

# 🔁 SESSION STATE INIT
if "prospecting_scores" not in st.session_state:
    load_scores()
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
        save_scores()

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
        save_scores()

# 🌟 TITLE
st.title("🔰 Skyline Summit Unit Champion Tracker 🔰")

# 🧲 TABS
tab1, tab2 = st.tabs(["🧲 Prospecting Champion", "💼 Recruitment Champion"])

# 🔷 PROSPECTING
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
            save_scores()
            st.success("Points updated.")

    col1, col2, col3 = st.columns(3)
    if col1.button("Undo"):
        undo()
    if col2.button("Redo"):
        redo()
    if col3.button("Clear All"):
        push_undo()
        st.session_state.prospecting_scores = {agent: 0 for agent in agents}
        save_scores()
        st.success("Scores cleared.")

    df_pro = pd.DataFrame(st.session_state.prospecting_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_pro)
    st.bar_chart(df_pro.set_index("Agent"))

# 🔶 RECRUITMENT
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
            save_scores()
            st.success("Points updated.")

    col1, col2, col3 = st.columns(3)
    if col1.button("Undo", key="undo2"):
        undo()
    if col2.button("Redo", key="redo2"):
        redo()
    if col3.button("Clear All", key="clear2"):
        push_undo()
        st.session_state.recruitment_scores = {agent: 0 for agent in agents}
        save_scores()
        st.success("Scores cleared.")

    df_rec = pd.DataFrame(st.session_state.recruitment_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_rec)
    st.bar_chart(df_rec.set_index("Agent"))

# 🟢 SYNC BUTTON
if st.button("📤 Sync to Google Sheets"):
    save_to_gsheet()
    st.success("Data synced to Google Sheets!")
