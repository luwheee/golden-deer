import streamlit as st
import pandas as pd
import copy
from datetime import date

# Agents list
agents = [
    "Louie Bartolome", "Riley Peñaflorida", "Dominick Xavier Alonso Bandin",
    "Jesica Anna Mikaela Latar", "Jona Alcazaren", "Luis De Guzman",
    "Maribelle Rosal", "Nicole Daep", "Sofiah Morcilla", "Winston Pasia"
]

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

# Session state initialization
if "prospecting_scores" not in st.session_state:
    st.session_state.prospecting_scores = {agent: 0 for agent in agents}
if "recruitment_scores" not in st.session_state:
    st.session_state.recruitment_scores = {agent: 0 for agent in agents}
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []
if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = []

# Save state to stack for undo/redo
def push_undo():
    snapshot = {
        "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
        "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
    }
    st.session_state.undo_stack.append(snapshot)
    st.session_state.redo_stack.clear()

# Undo and Redo functions
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

# Title
st.title("🔰 Skyline Summit Unit Champion Tracker 🔰")

# Tabs
tab1, tab2 = st.tabs(["🧲 Prospecting Champion", "💼 Recruitment Champion"])

# Prospecting
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
            st.success("Points updated.")

    col1, col2, col3 = st.columns(3)
    if col1.button("Undo"):
        undo()
    if col2.button("Redo"):
        redo()
    if col3.button("Clear All"):
        push_undo()
        st.session_state.prospecting_scores = {agent: 0 for agent in agents}
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
    if submitted:
        if selected_agents:
            push_undo()
            for agent in selected_agents:
                for activity, count in counts.items():
                    st.session_state.recruitment_scores[agent] += recruitment_points[activity] * count
            st.success("Points updated.")

    col1, col2, col3 = st.columns(3)
    if col1.button("Undo", key="undo2"):
        undo()
    if col2.button("Redo", key="redo2"):
        redo()
    if col3.button("Clear All", key="clear2"):
        push_undo()
        st.session_state.recruitment_scores = {agent: 0 for agent in agents}
        st.success("Scores cleared.")

    df_rec = pd.DataFrame(st.session_state.recruitment_scores.items(), columns=["Agent", "Points"]).sort_values(by="Points", ascending=False)
    st.dataframe(df_rec)
    st.bar_chart(df_rec.set_index("Agent"))
