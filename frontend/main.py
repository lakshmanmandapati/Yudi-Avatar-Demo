import streamlit as st
import requests
from io import BytesIO
import base64

st.set_page_config(page_title="Yudi Avatar Demo", layout="centered")

st.title("🎙️ Yudi Avatar Demo")

# Chat container
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_box = st.container()

# Record audio
st.info("Click record, speak, then press Stop to send audio")

audio_file = st.file_uploader("Upload your voice (or record externally)", type=["wav", "mp3", "webm"])

if audio_file:
    # Send audio to STT
    files = {"file": audio_file.getvalue()}
    stt_res = requests.post("http://localhost:8000/stt", files=files).json()
    user_text = stt_res.get("text", "")
    lang = stt_res.get("language", "en")
    st.session_state.messages.append(("user", user_text))

    # Send text to chat endpoint
    chat_res = requests.post("http://localhost:8000/chat", json={"message": user_text}).json()
    yudi_text = chat_res.get("reply", "")
    st.session_state.messages.append(("yudi", yudi_text))

    # TTS
    tts_res = requests.post("http://localhost:8000/tts", json={"text": yudi_text, "language": lang})
    audio_bytes = BytesIO(tts_res.content)

    # Play audio in Streamlit
    st.audio(audio_bytes, format="audio/wav")

# Display chat messages
with chat_box:
    for sender, msg in st.session_state.messages:
        if sender == "user":
            st.markdown(f"<div style='text-align:right;background-color:#4caf50;color:white;padding:10px;border-radius:10px;margin:5px 0;'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div style='text-align:left;background-color:#e0e0e0;color:black;padding:10px;border-radius:10px;margin:5px 0;'>{msg}</div>", unsafe_allow_html=True)
