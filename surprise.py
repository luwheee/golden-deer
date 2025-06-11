import streamlit as st

# --- Page Config ---
st.set_page_config(page_title="Surprise for Commander Cha 💖", layout="centered")

# --- GitHub-hosted Image ---
bg_image_url = "https://raw.githubusercontent.com/your-username/your-repo/main/Louie.jpg"

# --- Custom CSS with Background ---
custom_css = f"""
<style>
body {{
    background: url("{bg_image_url}") no-repeat center center fixed;
    background-size: cover;
    font-family: 'Comic Sans MS', cursive, sans-serif;
}}

.video-message-container {{
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2rem;
    margin-top: 2rem;
    flex-wrap: wrap;
}}

.video-box iframe {{
    border: none;
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}}

.message-box {{
    text-align: center;
    font-size: 22px;
    color: #d6336c;
    background-color: rgba(255, 240, 246, 0.9);
    padding: 1.5rem;
    border-radius: 1rem;
    max-width: 500px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    animation: fadeIn 2s ease-in-out;
}}

@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
</style>
"""

# --- Inject CSS ---
st.markdown(custom_css, unsafe_allow_html=True)

# --- Header ---
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
    st.markdown("""
    <div class="video-message-container">
        <div class="video-box">
            <iframe src="https://drive.google.com/file/d/18ypDybhzZPxVxfHmld5x_oNnilSQrxan/preview" width="480" height="270" allow="autoplay"></iframe>
        </div>
        <div class="message-box">
            Hi baby, first time to try this but yeah—it was a success! 💝<br><br>
            <strong>Happy Monthsary 💖</strong><br><br>
            More love, care, away, and money to come.<br>
            I love you so much! 💕
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.balloons()
