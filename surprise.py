import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Surprise for Commander Cha 💖", layout="centered")

# --- GitHub-hosted Image ---
BG_IMAGE_URL = "https://raw.githubusercontent.com/luwheee/golden-deer/main/Louie.jpg"

# --- Display the Background Image ---
st.image(BG_IMAGE_URL, use_column_width=True)

# --- Main Content ---
st.markdown("### 💖 Surprise for Commander Cha 💖")
st.markdown("## A little gift from your baby 💕")

# --- Reveal Logic ---
if "show_video" not in st.session_state:
    st.session_state["show_video"] = False

if not st.session_state["show_video"]:
    if st.button("🎁 Click the gift!"):
        st.session_state["show_video"] = True

# --- Video and Message Display ---
if st.session_state["show_video"]:
    st.markdown(f"""
    <div style="text-align: center;">
        <iframe src="https://drive.google.com/file/d/18ypDybhzZPxVxfHmld5x_oNnilSQrxan/preview" width="480" height="270" allow="autoplay"></iframe>
        <div style="margin-top: 20px; font-size: 22px; color: #d6336c;">
            Hi baby, first time to try this but yeah—it was a success! 💝<br><br>
            <strong>Happy Monthsary 💖</strong><br><br>
            More love, care, away, and money to come.<br>
            I love you so much! 💕
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()
