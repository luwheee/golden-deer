import streamlit as st

# --- Page Configuration ---
st.set_page_config(page_title="Surprise for Commander Cha 💖", layout="centered")

# --- Constants ---
BG_IMAGE_URL = "https://raw.githubusercontent.com/luwheee/golden-deer/main/Louie.jpg"
VIDEO_URL = "https://drive.google.com/file/d/18ypDybhzZPxVxfHmld5x_oNnilSQrxan/preview"

# --- Styles ---
def apply_custom_styles():
    custom_css = f"""
    <style>
        body {{
            background: url("{BG_IMAGE_URL}") no-repeat center center fixed;
            background-size: cover;
            font-family: 'Comic Sans MS', cursive, sans-serif;
        }}
        
        .container {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
            margin-top: 2rem;
        }}

        .video-box iframe {{
            border: none;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}

        .message-box {{
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
    st.markdown(custom_css, unsafe_allow_html=True)

# --- Main UI ---
def main():
    apply_custom_styles()
    
    st.markdown("### 💖 Surprise for Commander Cha 💖")
    st.markdown("## A little gift from your baby 💕")

    if "show_video" not in st.session_state:
        st.session_state["show_video"] = False

    if not st.session_state["show_video"]:
        if st.button("🎁 Click the gift!"):
            st.session_state["show_video"] = True

    if st.session_state["show_video"]:
        display_surprise()

# --- Surprise Content ---
def display_surprise():
    st.markdown(f"""
    <div class="container">
        <div class="video-box">
            <iframe src="{VIDEO_URL}" width="480" height="270" allow="autoplay"></iframe>
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

# Run the app
if __name__ == "__main__":
    main()
