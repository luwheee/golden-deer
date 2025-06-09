import streamlit as st
import pandas as pd
import copy

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

# Initialize session state variables
if "prospecting_scores" not in st.session_state:
    st.session_state.prospecting_scores = {agent: 0 for agent in agents}
if "recruitment_scores" not in st.session_state:
    st.session_state.recruitment_scores = {agent: 0 for agent in agents}
if "undo_stack" not in st.session_state:
    st.session_state.undo_stack = []
if "redo_stack" not in st.session_state:
    st.session_state.redo_stack = []
if "show_pros_confirm" not in st.session_state:
    st.session_state.show_pros_confirm = False
if "show_rec_confirm" not in st.session_state:
    st.session_state.show_rec_confirm = False

def save_state():
    snapshot = {
        "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
        "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
    }
    st.session_state.undo_stack.append(snapshot)
    st.session_state.redo_stack.clear()

def undo():
    if st.session_state.undo_stack:
        snapshot = st.session_state.undo_stack.pop()
        st.session_state.redo_stack.append({
            "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
            "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
        })
        st.session_state.prospecting_scores = snapshot["prospecting"]
        st.session_state.recruitment_scores = snapshot["recruitment"]

def redo():
    if st.session_state.redo_stack:
        snapshot = st.session_state.redo_stack.pop()
        st.session_state.undo_stack.append({
            "prospecting": copy.deepcopy(st.session_state.prospecting_scores),
            "recruitment": copy.deepcopy(st.session_state.recruitment_scores)
        })
        st.session_state.prospecting_scores = snapshot["prospecting"]
        st.session_state.recruitment_scores = snapshot["recruitment"]

# Custom CSS for better UI
st.markdown("""
<style>
    .stNumberInput > label {
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("Skyline Summit Unit Champion Tracker")

tab1, tab2 = st.tabs(["🧲 Prospecting Champion", "💼 Recruitment Champion"])

with tab1:
    st.subheader("Update Prospecting Points")
    selected_agents_pros = st.multiselect("Select agents", agents, key="pros_agents", help="Select agents to update points")

    with st.form("prospecting_form"):
        st.markdown("### Enter Activity Counts (0 = None)")

        pros_inputs = {}
        for label, pts in prospecting_points.items():
            pros_inputs[label] = st.number_input(
                f"{label} (+{pts} pts) ",
                min_value=0,
                step=1,
                key=f"pros_input_{label}",
                help=f"Points per unit: {pts}"
            )

        submitted = st.form_submit_button("✅ Submit")  # <-- no key here

        if submitted:
            if not selected_agents_pros:
                st.warning("Please select at least one agent.")
            else:
                with st.spinner("Updating points..."):
                    save_state()
                    for agent in selected_agents_pros:
                        for label, multiplier in pros_inputs.items():
                            st.session_state.prospecting_scores[agent] += prospecting_points[label] * multiplier
                st.balloons()
                st.success("Prospecting points updated successfully!")

    col1, col2, col3 = st.columns([1,1,4])
    if col1.button("↩️ Undo", key="pros_undo"):
        undo()
    if col2.button("↪️ Redo", key="pros_redo"):
        redo()

    if col3.button("🧼 Clear Prospecting Scores", key="pros_clear"):
        st.session_state.show_pros_confirm = True

    if st.session_state.show_pros_confirm:
        st.warning("Are you sure you want to clear all prospecting scores? This action cannot be undone.")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Yes, Clear Prospecting Scores", key="pros_clear_confirm"):
                save_state()
                st.session_state.prospecting_scores = {agent: 0 for agent in agents}
                st.session_state.show_pros_confirm = False
                st.success("Prospecting scores cleared.")
        with c2:
            if st.button("Cancel", key="pros_clear_cancel"):
                st.session_state.show_pros_confirm = False

    st.markdown("### 🧲 Prospecting Leaderboard")
    df_pro = pd.DataFrame(st.session_state.prospecting_scores.items(), columns=["Agent", "Points"])
    df_pro = df_pro.sort_values(by="Points", ascending=False)
    st.dataframe(df_pro)

    st.bar_chart(df_pro.set_index("Agent"))

    st.download_button("📥 Download Leaderboard", df_pro.to_csv(index=False), "prospecting_leaderboard.csv", "text/csv")

with tab2:
    st.subheader("Update Recruitment Points")
    selected_agents_rec = st.multiselect("Select agents", agents, key="rec_agents", help="Select agents to update points")

    with st.form("recruitment_form"):
        st.markdown("### Enter Activity Counts (0 = None)")

        rec_inputs = {}
        for label, pts in recruitment_points.items():
            rec_inputs[label] = st.number_input(
                f"{label} (+{pts} pts) ",
                min_value=0,
                step=1,
                key=f"rec_input_{label}",
                help=f"Points per unit: {pts}"
            )

        submitted2 = st.form_submit_button("✅ Submit")  # <-- no key here

        if submitted2:
            if not selected_agents_rec:
                st.warning("Please select at least one agent.")
            else:
                with st.spinner("Updating points..."):
                    save_state()
                    for agent in selected_agents_rec:
                        for label, multiplier in rec_inputs.items():
                            st.session_state.recruitment_scores[agent] += recruitment_points[label] * multiplier
                st.balloons()
                st.success("Recruitment points updated successfully!")

    col4, col5, col6 = st.columns([1,1,4])
    if col4.button("↩️ Undo", key="rec_undo"):
        undo()
    if col5.button("↪️ Redo", key="rec_redo"):
        redo()

    if col6.button("🧼 Clear Recruitment Scores", key="rec_clear"):
        st.session_state.show_rec_confirm = True

    if st.session_state.show_rec_confirm:
        st.warning("Are you sure you want to clear all recruitment scores? This action cannot be undone.")
        c3, c4 = st.columns(2)
        with c3:
            if st.button("Yes, Clear Recruitment Scores", key="rec_clear_confirm"):
                save_state()
                st.session_state.recruitment_scores = {agent: 0 for agent in agents}
                st.session_state.show_rec_confirm = False
                st.success("Recruitment scores cleared.")
        with c4:
            if st.button("Cancel", key="rec_clear_cancel"):
                st.session_state.show_rec_confirm = False

    st.markdown("### 💼 Recruitment Leaderboard")
    df_rec = pd.DataFrame(st.session_state.recruitment_scores.items(), columns=["Agent", "Points"])
    df_rec = df_rec.sort_values(by="Points", ascending=False)
    st.dataframe(df_rec)

    st.bar_chart(df_rec.set_index("Agent"))

    st.download_button("📥 Download Leaderboard", df_rec.to_csv(index=False), "recruitment_leaderboard.csv", "text/csv")
