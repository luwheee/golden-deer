import streamlit as st
import base64
import time

# --- Page Config ---
st.set_page_config(page_title="Surprise for Commander Cha 💖", layout="centered")

# --- Custom CSS ---
custom_css = """
<style>
body {
    background: linear-gradient(to top right, #ffe6f0, #ffe6ff);
    font-family: 'Comic Sans MS', cursive, sans-serif;
}
.video-message-container {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 2rem;
    margin-top: 2rem;
}
.video-box {
    flex: 1;
}
.message-box {
    flex: 1;
    text-align: center;
    font-size: 22px;
    color: #d6336c;
    background-color: #fff0f6;
    padding: 1.5rem;
    border-radius: 1rem;
    max-width: 500px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    animation: fadeIn 2s ease-in-out;
}
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Title and intro
st.markdown("### 💖 Surprise for Commander Cha 💖")
st.markdown("## A little gift from your baby 💕")

# Session flag for video reveal
if "show_video" not in st.session_state:
    st.session_state["show_video"] = False

# Gift button + countdown animation
if not st.session_state["show_video"]:
    if st.button("🎁 Click the gift!"):
        countdown = st.empty()
        for i in reversed(range(1, 4)):
            countdown.markdown(f"<h1 style='text-align:center;'>⏳ {i}...</h1>", unsafe_allow_html=True)
            time.sleep(1)
        countdown.empty()
        st.session_state["show_video"] = True

# Video reveal alongside message (both appear together)
if st.session_state["show_video"]:
    with open("0-02-06-wheeeee.mp4", "rb") as video_file:
        video_bytes = video_file.read()
        video_base64 = base64.b64encode(video_bytes).decode()
    
    video_html = f"""
    <div class="video-message-container">
        <div class="video-box">
            <video width="480" height="270" autoplay muted controls playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
        </div>
        <div class="message-box">
            Hi baby, first time to try this but yeah—it was a success! 💝<br><br>
            <strong>Happy Monthsary 💖</strong><br><br>
            More love, care, away, and money to come.<br>
            I love you so much! 💕
        </div>
    </div>
    """
    
    st.markdown(video_html, unsafe_allow_html=True)
    st.balloons()