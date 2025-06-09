import streamlit as st
import pandas as pd
import copy
import json
import os
from datetime import date

# --- Constants ---
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

DATE_TODAY = date.today().isoformat()
SAVE_FILE = f"leaderboard_data_{DATE_TODAY}.json"

# --- Helper Functions ---

def load_data():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

def save_data():
    data = {
        "prospecting": st.session_state.prospecting_scores,
        "recruitment": st.session_state.recruitment_scores
    }
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

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
        save_data()

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
        save_data()

# --- Initialize session state variables ---
if "prospecting_scores" not in st.session_state:
    st.session_state.prospecting_scores = {agent: 0 for agent in agents}

if "recruitment_scores" not in st.session_state:
    st.session_state.recruitment_scores = {agent: 0 for agent in agents}

if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []

if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = []

# Initialize input counters for prospecting
for activity in prospecting_points.keys():
    key = f"prospecting_{activity}"
    if key not in st.session_state:
        st.session_state[key] = 0

# Initialize input counters for recruitment
for activity in recruitment_points.keys():
    key = f"recruitment_{activity}"
    if key not in st.session_state:
        st.session_state[key] = 0

# --- UI ---

st.title("\U0001F530 Skyline Summit Unit Champion Tracker \U0001F530")

tab1, tab2 = st.tabs(["🧲 Prospecting Champion", "💼 Recruitment Champion"])

with tab1:
    st.subheader("Update Prospecting Points")

    # Single agent selectbox (only one can be chosen)
    selected_agent = st.selectbox("Select an agent", agents, key="prospect_agent")

    with st.form("pros_form"):
        counts = {}
        for activity, pts in prospecting_points.items():
            key = f"prospecting_{activity}"
            counts[activity] = st.number_input(f"{activity} (+{pts})", min_value=0, step=1, key=key)

        submitted = st.form_submit_button("Submit")

    if submitted:
        push_undo()
        for activity, count in counts.items():
            st.session_state.prospecting_scores[selected_agent] += prospecting_points[activity] * count
        save_data()
        st.success(f"Prospecting points updated for {selected_agent}!")

        # Reset inputs to zero safely
        for activity in prospecting_points.keys():
            st.session_state[f"prospecting_{activity}"] = 0

        st.experimental_rerun()  # Refresh to update UI and reset inputs

    c1, c2, c3 = st.columns(3)
    if c1.button("Undo"):
        undo()
    if c2.button("Redo"):
        redo()
    if c3.button("Clear All"):
        push_undo()
        st.session_state.prospecting_scores = {agent: 0 for agent in agents}
        save_data()
        st.success("All prospecting scores cleared!")

    # Show leaderboard
    df_pro = pd.DataFrame(st.session_state.prospecting_scores.items(), columns=["Agent", "Points"])
    df_pro = df_pro.sort_values("Points", ascending=False)
    st.dataframe(df_pro)
    st.bar_chart(df_pro.set_index("Agent"))

with tab2:
    st.subheader("Update Recruitment Points")

    selected_agent = st.selectbox("Select an agent", agents, key="recruit_agent")

    with st.form("rec_form"):
        counts = {}
        for activity, pts in recruitment_points.items():
            key = f"recruitment_{activity}"
            counts[activity] = st.number_input(f"{activity} (+{pts})", min_value=0, step=1, key=key)

        submitted = st.form_submit_button("Submit")

    if submitted:
        push_undo()
        for activity, count in counts.items():
            st.session_state.recruitment_scores[selected_agent] += recruitment_points[activity] * count
        save_data()
        st.success(f"Recruitment points updated for {selected_agent}!")

        # Reset inputs
        for activity in recruitment_points.keys():
            st.session_state[f"recruitment_{activity}"] = 0

        st.experimental_rerun()

    c1, c2, c3 = st.columns(3)
    if c1.button("Undo", key="undo2"):
        undo()
    if c2.button("Redo", key="redo2"):
        redo()
    if c3.button("Clear All", key="clear2"):
        push_undo()
        st.session_state.recruitment_scores = {agent: 0 for agent in agents}
        save_data()
        st.success("All recruitment scores cleared!")

    df_rec = pd.DataFrame(st.session_state.recruitment_scores.items(), columns=["Agent", "Points"])
    df_rec = df_rec.sort_values("Points", ascending=False)
    st.dataframe(df_rec)
    st.bar_chart(df_rec.set_index("Agent"))
