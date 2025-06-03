import streamlit as st
from gtts import gTTS
from io import BytesIO
import base64
import time

st.set_page_config(page_title="LAB's Text to Speech Tool", layout="wide")

# Sidebar with info and navigation
st.sidebar.title("🎙️ LAB's Text to Speech")
st.sidebar.write("""
Welcome!  
Use this tool to convert your text into spoken audio.  
Choose your language, speed, and press **Convert to Speech**.  
Made with ❤️ by LAB.
""")

# Main title
st.title("🎧 LAB's Text to Speech Tool")

# Language options with flag emojis
language_options = {
    "🇺🇸 English (US)" : "en",
    "🇬🇧 English (UK)" : "en-uk",
    "🇵🇭 Filipino"     : "tl",
    "🇯🇵 Japanese"     : "ja",
    "🇪🇸 Spanish"      : "es",
    "🇫🇷 French"       : "fr",
    "🇩🇪 German"       : "de",
    "🇰🇷 Korean"       : "ko",
    "🇮🇹 Italian"      : "it",
    "🇵🇹 Portuguese"   : "pt",
    "🇮🇳 Hindi"        : "hi"
}

# Input text
text = st.text_area("Enter text to convert to speech:", height=150)

# Select language with flags
language = st.selectbox("Choose language & voice style:", list(language_options.keys()))

# Speed toggle
speed = st.radio("Speed:", ["Normal", "Fast"], index=0)
slow = False if speed == "Fast" else True

# Generate button and spinner
if st.button("Convert to Speech"):
    if text.strip() == "":
        st.warning("⚠️ Please enter some text first.")
    else:
        with st.spinner("Generating speech... 🎤"):
            try:
                lang_code = language_options[language]
                tts = gTTS(text=text, lang=lang_code, slow=slow)
                audio_fp = BytesIO()
                tts.write_to_fp(audio_fp)
                audio_fp.seek(0)
                st.success("✅ Speech generated successfully!")
                st.audio(audio_fp.read(), format="audio/mp3")

                # Reset stream for download button
                audio_fp.seek(0)
                st.download_button(
                    label="🎵 Download MP3",
                    data=audio_fp,
                    file_name="speech.mp3",
                    mime="audio/mp3",
                    help="Click to download the audio file"
                )
            except Exception as e:
                st.error(f"❌ Something went wrong: {e}")

# Footer
st.markdown("""
---
<p style="text-align:center; font-size:12px; color:gray;">
Made with ❤️ by LAB | Powered by Streamlit & gTTS
</p>
""", unsafe_allow_html=True)
