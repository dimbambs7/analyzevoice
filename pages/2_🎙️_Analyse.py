from __future__ import division
import re
import queue
import pyaudio
import gspread
import keyboard as kb
from oauth2client.service_account import ServiceAccountCredentials
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
import streamlit as st
from streamlit_extras.stoggle import stoggle
from streamlit_webrtc import WebRtcMode, webrtc_streamer

# Définir vos secrets et autres configurations ici
speech_secrets = st.secrets["connections_gstt"]
secrets_dict = st.secrets["connections_gsheets"]

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets_dict, scope)
client = gspread.authorize(creds)

st.set_page_config(page_title="Analyse", page_icon="🎙️")

class MicrophoneStream:
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            stream_callback=self._fill_buffer,
        )
        self.closed = False
        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)

def get_shortcuts(user_mail):
    main_sheet = client.open("Database")
    sheet_title = f"Shortcut_{user_mail}"
    worksheet = main_sheet.worksheet(sheet_title)
    all_records = worksheet.get_all_records()
    shortcuts = [{k: v for k, v in record.items() if k in ['shortcut_key', 'shortcut_letter']} for record in all_records]
    return shortcuts

def stt(transcript, shortcuts):
    for shortcut in shortcuts:
        shortcut_key = shortcut['shortcut_key']
        shortcut_letter = shortcut['shortcut_letter']
        if any(shortcut_key in word for word in transcript.split()):
            kb.press(shortcut_letter)
            #st.write(f"Pressed shortcut: {shortcut_letter}")
            return True
    return False

def listen_print_loop(responses, shortcuts, mode):
    num_chars_printed = 0

    for response in responses:
        if not response.results:
            continue

        result = response.results[0]
        if not result.alternatives:
            continue

        transcript = result.alternatives[0].transcript

        if mode == "Rapide ☄️":
            if not result.is_final:
                st.write(transcript)
                stt(transcript, shortcuts)
        elif mode == "Précis 🎯":
            if result.is_final:
                st.write(transcript)
                stt(transcript, shortcuts)

        num_chars_printed = 0

        if re.search(r"\b(exit|quit)\b", transcript, re.I):
            print("Exiting..")
            break

        num_chars_printed = 0

def streaming_recognize(shortcuts, mode):
    credentials = service_account.Credentials.from_service_account_info(speech_secrets)
    client_speech = speech.SpeechClient(credentials=credentials)
    RATE = 16000
    CHUNK = int(RATE / 10)

    with MicrophoneStream(RATE, CHUNK) as stream:
        audio_generator = stream.generator()
        requests = (speech.StreamingRecognizeRequest(audio_content=content) for content in audio_generator)

        streaming_config = speech.StreamingRecognitionConfig(
            config=speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code="fr-FR"
            ),
            interim_results=True
        )

        responses = client_speech.streaming_recognize(config=streaming_config, requests=requests)
        listen_print_loop(responses, shortcuts, mode)

def home():
    if 'run' not in st.session_state:
        st.session_state['run'] = False

    user_mail = st.session_state.useremail

    if not st.session_state['signedout']:
        st.write(":red[Veuillez vous connecter]")
    else:
        st.markdown("""
        <style>
            header {
                visibility: hidden;
            }
            .css-eh5xgm.e1ewe7hr3,
            .css-cio0dv.e1g8pov61 {
                visibility: hidden;
            }
        </style>
        """, unsafe_allow_html=True)
        st.title("🎙️ Analyse")
        st.write("---")
        st.subheader("Mode")
        stoggle(
            "Précision sur les modes !",
            """<br>Le mode rapide ☄️ : Il permet d'avoir une retranscription rapide de ce que vous dit mais il est moins précis.<br><br>Le mode précis 🎯 : Il permet d'avoir une retranscription précise de ce que vous dîtes mais il est moins rapide.""",
        )
        st.write("")
        mode_options = ["Rapide ☄️", "Précis 🎯"]
        mode = st.select_slider("Choisissez un mode", options=mode_options)
        st.write(f"Le mode {mode} est activé !")
        st.write("---")
        st.write("Débutez votre analyse en cliquant sur le bouton Start. Lorsque vous avez fini, veuillez cliquer sur Stop.")

        webrtc_ctx = webrtc_streamer(
            key="speech-to-text",
            mode=WebRtcMode.SENDONLY,
            audio_receiver_size=1024,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
            media_stream_constraints={"video": False, "audio": True}
        )

        if not webrtc_ctx.state.playing:
            st.stop()

        status_indicator = st.empty()

        if webrtc_ctx.audio_receiver:
            shortcuts = get_shortcuts(user_mail)
            streaming_recognize(shortcuts, mode)

home()
