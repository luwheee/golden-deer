# text_to_speech_app.py

import streamlit as st
from gtts import gTTS
import os

st.set_page_config(page_title="LAB's Text-to-Speech", page_icon="🗣️", layout="centered")
st.title("🗣️ LAB's Text to Speech Tool")

# Input text
text = st.text_area("Enter text to convert to speech:")

# Language options
language_options = {
    "English (US)": "en",
    "English (UK)": "en-uk",
    "Filipino": "tl",
    "Japanese": "ja",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Korean": "ko",
    "Italian": "it",
    "Portuguese": "pt",
    "Hindi": "hi"
}

language = st.selectbox("Choose language & voice style:", list(language_options.keys()))

# Speed selection
speed = st.radio("Speech Speed:", ["Normal", "Fast"])
slow = False if speed == "Fast" else True

if st.button("🔊 Convert to Speech"):
    if not text.strip():
        st.warning("⚠️ Please enter some text first.")
    else:
        try:
            lang_code = language_options[language]
            tts = gTTS(text=text, lang=lang_code, slow=slow)
            filename = "output.mp3"
            tts.save(filename)

            st.success("✅ Speech generated successfully!")
            st.audio(filename, format="audio/mp3")

            # Download button
            with open(filename, "rb") as f:
                audio_bytes = f.read()
            st.download_button(label="⬇️ Download MP3", data=audio_bytes, file_name="speech.mp3", mime="audio/mp3")

        except Exception as e:
            st.error(f"❌ Something went wrong: {e}")
