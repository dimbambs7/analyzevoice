from __future__ import division
import re
import sys
import pyaudio
import queue
from pynput.keyboard import Controller
from google.cloud import speech_v1p1beta1 as speech
from google.oauth2 import service_account
from google.cloud import speech
import streamlit as st
from streamlit_extras.stoggle import stoggle
import pymysql
from config import DB_CONFIG

db = pymysql.connect(**DB_CONFIG)
cursor = db.cursor()

def get_shortcuts(user_id):
    query = f"SELECT shortcut_key, shortcut_letter FROM table_shortcut_{user_id}"
    cursor.execute(query)
    shortcuts = cursor.fetchall()
    return shortcuts
    #return {shortcut['shortcut_key']: shortcut['shortcut_letter'] for shortcut in shortcuts}
    
def stt(transcript, shortcuts):
    for shortcut in shortcuts:
        shortcut_key = shortcut['shortcut_key']
        shortcut_letter = shortcut['shortcut_letter']
        if any(shortcut_key in word for word in transcript.split()):
            Controller().press(shortcut_letter)
            Controller().release(shortcut_letter) 
            return True
    return False

def home():
    st.set_page_config(page_title="Analyse", page_icon="🎙️")
    global selected_mode
    if 'run' not in st.session_state:
        st.session_state['run'] = False

    def start_listening():
        st.session_state['run'] = True

    def stop_listening():
        st.session_state['run'] = False

    if not st.session_state['signedout']:
        st.write(":red[Veuillez vous connecter]")
    else:
        st.markdown("""
<style>
header
{
    visibility: hidden;
}
.css-eh5xgm.e1ewe7hr3
{
    visibility: hidden;
}
.css-cio0dv.e1g8pov61
{
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)
        st.title("🎙️ Analyse")
        st.write("---")
        st.subheader("Mode")
        stoggle(
            "Précision sur les modes !",
            """Le mode rapide ☄️ : Il permet d'avoir une retranscription rapide de ce que vous dit mais il est moins précis.<br>Le mode précis 🎯 : Il permet d'avoir une retranscription précise de ce que vous dîtes mais il est moins rapide.""",
        )
        st.write("")
        mode_options = ["Rapide ☄️", "Précis 🎯"]
        mode = st.select_slider("Choissisez un mode", options=mode_options)
        selected_mode = mode
        st.write(f"Le mode {mode} est activé !")
        st.write("---")
        st.write("Débutez votre analyse en cliquant sur le bouton Start. Lorsque vous avez fini, veuillez cliquer sur Stop.")
        start, stop = st.columns(2)
        start.button('⏯️ Start', on_click=start_listening)
        stop.button('⏹️ Stop', on_click=stop_listening)
        user_id = st.session_state['user_id']
        shortcuts = get_shortcuts(user_id)
        credentials_path = "/Users/dimbambs/Desktop/Personnel/Python/Perso/AnalyzeVoice/keys.json"

        credentials = service_account.Credentials.from_service_account_file(credentials_path)

        client = speech.SpeechClient(credentials=credentials)

        # Audio recording parameters
        RATE = 16000
        CHUNK = int(RATE / 10)  # 100ms

        class MicrophoneStream(object):
            """Opens a recording stream as a generator yielding the audio chunks."""

            def __init__(self, rate, chunk):
                self._rate = rate
                self._chunk = chunk

                # Create a thread-safe buffer of audio data
                self._buff = queue.Queue()
                self.closed = True

            def __enter__(self):
                self._audio_interface = pyaudio.PyAudio()
                self._audio_stream = self._audio_interface.open(
                    format=pyaudio.paInt16,
                    # The API currently only supports 1-channel (mono) audio
                    # https://goo.gl/z757pE
                    channels=1,
                    rate=self._rate,
                    input=True,
                    frames_per_buffer=self._chunk,
                    # Run the audio stream asynchronously to fill the buffer object.
                    # This is necessary so that the input device's buffer doesn't
                    # overflow while the calling thread makes network requests, etc.
                    stream_callback=self._fill_buffer,
                )

                self.closed = False

                return self

            def __exit__(self, type, value, traceback):
                self._audio_stream.stop_stream()
                self._audio_stream.close()
                self.closed = True
                # Signal the generator to terminate so that the client's
                # streaming_recognize method will not block the process termination.
                self._buff.put(None)
                self._audio_interface.terminate()

            def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
                """Continuously collect data from the audio stream, into the buffer."""
                self._buff.put(in_data)
                return None, pyaudio.paContinue

            def generator(self):
                while not self.closed:
                    # Use a blocking get() to ensure there's at least one chunk of
                    # data, and stop iteration if the chunk is None, indicating the
                    # end of the audio stream.
                    chunk = self._buff.get()
                    if chunk is None:
                        return
                    data = [chunk]

                    # Now consume whatever other data's still buffered.
                    while True:
                        try:
                            chunk = self._buff.get(block=False)
                            if chunk is None:
                                return
                            data.append(chunk)
                        except queue.Empty:
                            break

                    yield b"".join(data)

        def listen_print_loop(responses, shortcuts):
            """Iterates through server responses and prints them. f"\n {transcript + overwrite_chars}

            The responses passed is a generator that will block until a response
            is provided by the server.

            Each response may contain multiple results, and each result may contain
            multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
            print only the transcription for the top alternative of the top result.

            In this case, responses are provided for interim results as well. If the
            response is an interim one, print a line feed at the end of it, to allow
            the next result to overwrite it, until the response is a final one. For the
            final one, print a newline to preserve the finalized transcription.
            """
            global selected_mode
            num_chars_printed = 0

            for response in responses:
                if not response.results:
                    continue

                # The `results` list is consecutive. For streaming, we only care about
                # the first result being considered, since once it's `is_final`, it
                # moves on to considering the next utterance.
                result = response.results[0]
                if not result.alternatives:
                    continue

                # Display the transcription of the top alternative.
                transcript = result.alternatives[0].transcript

                # Display interim results, but with a carriage return at the end of the
                # line, so subsequent lines will overwrite them.
                #
                # If the previous result was longer than this one, we need to print
                # some extra spaces to overwrite the previous result
                #overwrite_chars = " " * (num_chars_printed - len(transcript))

                #if not result.is_final:
                    #sys.stdout.write(transcript + overwrite_chars + "\r")
                    #sys.stdout.flush()
                if selected_mode == "Rapide ☄️":
                    if not result.is_final:
                        st.markdown(transcript) #overwrite_chars
                        stt(transcript, shortcuts)
                elif selected_mode == "Précis 🎯":
                    if result.is_final:
                        st.markdown(transcript)
                        stt(transcript, shortcuts)

                    #num_chars_printed = len(transcript)

                #else:
                    #print(transcript + overwrite_chars)
                    #if selected_mode == "Précis 🎯":
                        #st.markdown(transcript + overwrite_chars)
                        #stt(transcript, shortcuts)

                    # Exit recognition if any of the transcribed phrases could be
                    # one of our keywords.
                    if re.search(r"\b(exit|quit)\b", transcript, re.I):
                        print("Exiting..")
                        break

                    num_chars_printed = 0

        def main():
            # See http://g.co/cloud/speech/docs/languages
            # for a list of supported languages.
            language_code = "fr-FR"  # a BCP-47 language tag

            client = speech.SpeechClient()
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=RATE,
                language_code=language_code,
            )

            streaming_config = speech.StreamingRecognitionConfig(
                config=config, interim_results=True
            )

            if st.session_state['run']:
                with MicrophoneStream(RATE, CHUNK) as stream:
                    audio_generator = stream.generator()
                    requests = (
                        speech.StreamingRecognizeRequest(audio_content=content)
                        for content in audio_generator
                    )

                    responses = client.streaming_recognize(streaming_config, requests)

                    # Now, put the transcription responses to use.
                    listen_print_loop(responses, shortcuts)

        main()

home()