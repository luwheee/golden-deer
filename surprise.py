import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Surprise for Commander Cha 💖", layout="centered")

# --- GitHub-hosted Background Image ---
BG_IMAGE_URL = "https://raw.githubusercontent.com/luwheee/golden-deer/main/Louie.jpg"

# --- Fullscreen Background with Styling ---
st.markdown(f"""
    <style>
    body {{
        background: url("{BG_IMAGE_URL}") no-repeat center center fixed;
        background-size: cover;
        font-family: 'Comic Sans MS', cursive;
    }}
    .main {{
        background-color: rgba(255, 255, 255, 0.85);
        padding: 2rem;
        border-radius: 1.5rem;
        max-width: 800px;
        margin: auto;
        margin-top: 3rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }}
    .center {{
        text-align: center;
    }}
    .message {{
        font-size: 22px;
        color: #d6336c;
        margin-top: 20px;
    }}
    </style>
""", unsafe_allow_html=True)

# --- Start Content Wrapper ---
st.markdown('<div class="main">', unsafe_allow_html=True)

# --- Header ---
st.markdown('<div class="center"><h3>💖 Surprise for Commander Cha 💖</h3><h4>A little gift from your baby 💕</h4></div>', unsafe_allow_html=True)

# --- Reveal Logic ---
if "show_video" not in st.session_state:
    st.session_state["show_video"] = False

if not st.session_state["show_video"]:
    if st.button("🎁 Click the gift!"):
        st.session_state["show_video"] = True

# --- Video and Message Display ---
if st.session_state["show_video"]:
    st.markdown("""
    <div class="center">
        <iframe src="https://drive.google.com/file/d/18ypDybhzZPxVxfHmld5x_oNnilSQrxan/preview" width="480" height="270" allow="autoplay"></iframe>
        <div class="message">
            Hi baby, first time to try this but yeah—it was a success! 💝<br><br>
            <strong>Happy Monthsary 💖</strong><br><br>
            More love, care, away, and money to come.<br>
            I love you so much! 💕
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.balloons()

# --- End Content Wrapper ---
st.markdown('</div>', unsafe_allow_html=True)
